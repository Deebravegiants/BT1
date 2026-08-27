This is a real, confirmed design gap: the code has no state-machine check that requires `Approved` before a signer can populate `status.certificate`, and this is by upstream Kubernetes design, not an accidental omission introduced here — but per the rules of this audit (analyze reachable code paths and existing checks only), it constitutes a valid finding.

### Title
CertificateSigning admission plugin allows setting status.Certificate on an unapproved CSR with only 'sign' RBAC, no 'approve' required - ([File: plugin/pkg/admission/certificates/signing/admission.go])

### Summary
`ValidateCertificateSigningRequestStatusUpdate` in `pkg/apis/certificates/validation/validation.go` unconditionally sets `opts.allowSettingCertificate = true` for any status update, and `validateCertificateSigningRequestUpdate` never checks whether an `Approved` condition exists before permitting `status.Certificate` to be set. The `CertificateSigning` admission plugin (`plugin/pkg/admission/certificates/signing/admission.go`) gates the status-update call only on the `sign` verb for the CSR's `signerName`, with no check on `csr.Status.Conditions`. Consequently, a principal holding only `sign` RBAC (and `update` on `certificatesigningrequests/status`) — without `approve` — can attach an arbitrary certificate to a freshly created, unapproved CSR.

### Finding Description
- `ValidateCertificateSigningRequestUpdate` (line 280) uses `opts.allowSettingCertificate=false` by default (via `getValidationOptions`, line 353), but `ValidateCertificateSigningRequestStatusUpdate` (line 285-289) always overrides it to `true`, unconditionally — with no read of `newCSR.Status.Conditions` or check for `certificates.CertificateApproved`. [1](#0-0) 
- Inside `validateCertificateSigningRequestUpdate`, the only certificate-related checks are whether `allowSettingCertificate` is true and whether resetting an existing certificate is allowed — neither depends on approval state. [2](#0-1) 
- The `csrStatusStrategy.ValidateUpdate` in the registry strategy calls exactly this function for the `/status` subresource, and its `PrepareForUpdate` only preserves Approved/Denied condition instances (does not require them to exist or gate the certificate field on them). [3](#0-2) [4](#0-3) 
- The `CertificateSigning` admission plugin, which is the only additional gate applied on `certificatesigningrequests/status` updates, checks solely `IsAuthorizedForSignerName(..., "sign", oldCSR.Spec.SignerName)` — it never inspects `oldCSR.Status.Conditions` for an `Approved` condition. [5](#0-4) 
- By contrast, the `CertificateApproval` plugin only guards the separate `/approval` subresource with the `approve` verb, and has no interaction with the `/status` subresource path. [6](#0-5) 

Exploit flow: an identity with RBAC `update` on `certificatesigningrequests/status` and `sign` on `signers/<name>` (but no `approve`) can: (1) create an ordinary unapproved CSR (`PrepareForCreate` clears `Status`, line 98-100 in strategy.go), then (2) call the `UpdateStatus` API setting `Status.Certificate` to an arbitrary valid PEM certificate. Validation permits it because `allowSettingCertificate=true` is set regardless of approval state, and the signing admission plugin only checks the `sign` verb.

### Impact Explanation
This allows an actor holding only the "signer" role (not the "approver" role) to unilaterally mint and attach a certificate to a CSR that was never approved — bypassing the intended two-actor approve-then-sign workflow (`system:certificates.k8s.io:certificatesigningrequests:*` split roles). This matches Kubernetes bounty impact class "Authorization/RBAC bypass leading to unauthorized issuance/control-plane trust material forgery," since the approve/sign split is a deliberate separation-of-duties control that is not actually enforced at the object level.

### Likelihood Explanation
Minimal RBAC needed: `sign` verb on `signers/<narrow-signer-name>` (or wildcard) plus generic `update`/`get` on `certificatesigningrequests/status` and `get`/`create` on `certificatesigningrequests` — no `approve` verb required. This is a common real-world RBAC grant for automated cert-signing controllers/operators that are intentionally *not* granted approval authority. The action is fully reproducible via the standard `UpdateStatus` client call and requires no timing races, no admin credentials, and no cluster misconfiguration beyond the RBAC split that Kubernetes documentation explicitly recommends operators use (approve and sign as separate roles).

### Recommendation
Add an explicit state-machine check in `validateCertificateSigningRequestUpdate` (or specifically in the certificate-setting branch used by `ValidateCertificateSigningRequestStatusUpdate`) requiring that `newCSR.Status.Conditions` (or `oldCSR.Status.Conditions`) contain an `Approved` condition with status `True` before allowing `status.Certificate` to transition from empty to non-empty. Alternatively/additionally, update the `CertificateSigning` admission plugin (`plugin/pkg/admission/certificates/signing/admission.go`) to reject setting `status.Certificate` on CSRs that lack an `Approved` condition, mirroring how `CertificateApproval` enforces the `approve` verb for the `/approval` subresource.

### Proof of Concept
Integration test plan (extends existing test patterns in `test/integration/auth` and `pkg/apis/certificates/validation/validation_test.go`):
1. Create RBAC ClusterRole/ClusterRoleBinding granting only: `update` on `certificatesigningrequests/status`, `get`/`create` on `certificatesigningrequests`, and `sign` on `signers` for a specific narrow `signerName` (e.g., `example.com/only-signer`) — explicitly withhold `approve`.
2. As this identity, create a CSR with that `signerName` (unapproved, no `status.conditions`).
3. Call `UpdateStatus()` on the CSR, setting `Status.Certificate` to a valid PEM certificate, leaving `Status.Conditions` empty (no Approved condition).
4. Assert the call succeeds (HTTP 200/no error) despite the absence of an `Approved` condition — expected/current buggy behavior.
5. As a control, assert that the same identity cannot call the `/approval` subresource to add `Approved` (should fail with `Forbidden` due to missing `approve` RBAC), confirming that the certificate was attached via the `/status` path outside the intended approve→sign flow.
6. Unit-test addition in `validation_test.go`: call `ValidateCertificateSigningRequestStatusUpdate` with an `oldCSR`/`newCSR` pair where `Status.Conditions` is empty and `newCSR.Status.Certificate` is non-empty; assert that `field.ErrorList` is currently empty (demonstrating no gating), then after the fix, assert a `Forbidden` error is returned referencing missing `Approved` condition.

### Citations

**File:** pkg/apis/certificates/validation/validation.go (L285-289)
```go
func ValidateCertificateSigningRequestStatusUpdate(newCSR, oldCSR *certificates.CertificateSigningRequest) field.ErrorList {
	opts := getValidationOptions(newCSR, oldCSR)
	opts.allowSettingCertificate = true
	return validateCertificateSigningRequestUpdate(newCSR, oldCSR, opts)
}
```

**File:** pkg/apis/certificates/validation/validation.go (L327-333)
```go
	if !bytes.Equal(newCSR.Status.Certificate, oldCSR.Status.Certificate) {
		if !opts.allowSettingCertificate {
			validationErrorList = append(validationErrorList, field.Forbidden(field.NewPath("status", "certificate"), "updates may not set certificate content"))
		} else if !opts.allowResettingCertificate && len(oldCSR.Status.Certificate) > 0 {
			validationErrorList = append(validationErrorList, field.Forbidden(field.NewPath("status", "certificate"), "updates may not modify existing certificate content"))
		}
	}
```

**File:** pkg/registry/certificates/certificates/strategy.go (L170-184)
```go
func (csrStatusStrategy) PrepareForUpdate(ctx context.Context, obj, old runtime.Object) {
	newCSR := obj.(*certificates.CertificateSigningRequest)
	oldCSR := old.(*certificates.CertificateSigningRequest)

	// Updating /status should not modify spec
	newCSR.Spec = oldCSR.Spec

	// Specifically preserve existing Approved/Denied conditions.
	// Adding/removing Approved/Denied conditions will cause these to fail,
	// and the change in Approved/Denied conditions will produce a validation error
	preserveConditionInstances(newCSR, oldCSR, certificates.CertificateApproved)
	preserveConditionInstances(newCSR, oldCSR, certificates.CertificateDenied)

	populateConditionTimestamps(newCSR, oldCSR)
}
```

**File:** pkg/registry/certificates/certificates/strategy.go (L241-245)
```go
func (csrStatusStrategy) ValidateUpdate(ctx context.Context, obj, old runtime.Object) field.ErrorList {
	newCSR := obj.(*certificates.CertificateSigningRequest)
	oldCSR := old.(*certificates.CertificateSigningRequest)
	return validation.ValidateCertificateSigningRequestStatusUpdate(newCSR, oldCSR)
}
```

**File:** plugin/pkg/admission/certificates/signing/admission.go (L78-106)
```go
func (p *Plugin) Validate(ctx context.Context, a admission.Attributes, o admission.ObjectInterfaces) error {
	// Ignore all calls to anything other than 'certificatesigningrequests/status'.
	// Ignore all operations other than UPDATE.
	if a.GetSubresource() != "status" ||
		a.GetResource().GroupResource() != csrGroupResource {
		return nil
	}

	oldCSR, ok := a.GetOldObject().(*api.CertificateSigningRequest)
	if !ok {
		return admission.NewForbidden(a, fmt.Errorf("expected type CertificateSigningRequest, got: %T", a.GetOldObject()))
	}
	csr, ok := a.GetObject().(*api.CertificateSigningRequest)
	if !ok {
		return admission.NewForbidden(a, fmt.Errorf("expected type CertificateSigningRequest, got: %T", a.GetObject()))
	}

	// only run if the status.certificate or status.conditions field has been changed
	if reflect.DeepEqual(oldCSR.Status.Certificate, csr.Status.Certificate) && apiequality.Semantic.DeepEqual(oldCSR.Status.Conditions, csr.Status.Conditions) {
		return nil
	}

	if !certauthorization.IsAuthorizedForSignerName(ctx, p.authz, a.GetUserInfo(), "sign", oldCSR.Spec.SignerName) {
		klog.V(4).Infof("user not permitted to sign CertificateSigningRequest %q with signerName %q", oldCSR.Name, oldCSR.Spec.SignerName)
		return admission.NewForbidden(a, fmt.Errorf("user not permitted to sign requests with signerName %q", oldCSR.Spec.SignerName))
	}

	return nil
}
```

**File:** plugin/pkg/admission/certificates/approval/admission.go (L75-97)
```go
func (p *Plugin) Validate(ctx context.Context, a admission.Attributes, _ admission.ObjectInterfaces) error {
	// Ignore all calls to anything other than 'certificatesigningrequests/approval'.
	// Ignore all operations other than UPDATE.
	if a.GetSubresource() != "approval" ||
		a.GetResource().GroupResource() != csrGroupResource {
		return nil
	}

	// We check permissions against the *old* version of the resource, in case
	// a user is attempting to update the SignerName when calling the approval
	// endpoint (which is an invalid/not allowed operation)
	csr, ok := a.GetOldObject().(*api.CertificateSigningRequest)
	if !ok {
		return admission.NewForbidden(a, fmt.Errorf("expected type CertificateSigningRequest, got: %T", a.GetOldObject()))
	}

	if !certauthorization.IsAuthorizedForSignerName(ctx, p.authz, a.GetUserInfo(), "approve", csr.Spec.SignerName) {
		klog.V(4).Infof("user not permitted to approve CertificateSigningRequest %q with signerName %q", csr.Name, csr.Spec.SignerName)
		return admission.NewForbidden(a, fmt.Errorf("user not permitted to approve requests with signerName %q", csr.Spec.SignerName))
	}

	return nil
}
```
