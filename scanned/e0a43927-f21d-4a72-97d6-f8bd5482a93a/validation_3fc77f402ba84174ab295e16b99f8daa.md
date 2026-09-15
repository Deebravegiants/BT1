### Title
`ValidateGetSecretsRequest` wrongfully rejects a `GetSecrets` batch that is exactly at `MaxBatchSize` - (File: `core/capabilities/vault/validator.go`)

### Summary
`RequestValidator.ValidateGetSecretsRequest` uses `>=` instead of `>` when comparing the request batch length to `vaulttypes.MaxBatchSize`, causing legitimate requests containing exactly `MaxBatchSize` items to be rejected as if they exceeded the limit — the same off-by-one class described in the reference report (`length >= MAX` instead of `length > MAX`).

### Finding Description
In `core/capabilities/vault/validator.go`, `ValidateGetSecretsRequest` checks: [1](#0-0) 

```go
func (r *RequestValidator) ValidateGetSecretsRequest(ctx context.Context, request *vaultcommon.GetSecretsRequest) error {
	if len(request.Requests) == 0 {
		return errors.New("no GetSecret request specified in request")
	}
	if len(request.Requests) >= vaulttypes.MaxBatchSize {
		return fmt.Errorf("request batch size exceeds maximum of %d", vaulttypes.MaxBatchSize)
	}
``` [2](#0-1) 

This means a caller submitting a batch of exactly `vaulttypes.MaxBatchSize` items — which is by definition within the allowed maximum — is incorrectly rejected with "request batch size exceeds maximum of %d". This is confirmed by the existing test, which builds a batch of exactly `MaxBatchSize` and asserts it is rejected: [3](#0-2) 

By contrast, every other batch-size/length limiter in the same file (`MaxRequestBatchSizeLimiter.Check`, `MaxCiphertextLengthLimiter.Check`, `MaxIdentifierKeyLengthLimiter.Check`, etc., used in `validateWriteRequest`, `ValidateDeleteSecretsRequest`, `ValidateCiphertextSize`, `ValidateSecretIdentifier`) rely on `limits.BoundLimiter.Check`, whose semantics reject only when the value is strictly greater than the bound (`n > bound`), and are confirmed to accept a value exactly at the limit via tests such as "create accepts ciphertext at the limit": [4](#0-3) [5](#0-4) 

`ValidateGetSecretsRequest` is the sole inconsistent outlier that manually compares length using `>=` against `vaulttypes.MaxBatchSize` rather than delegating to a `Check`-style bound limiter, introducing the off-by-one boundary error.

### Impact Explanation
This is a functional/availability defect reachable from any unprivileged workflow or gateway caller invoking the vault capability's `GetSecrets` method (`MethodGetSecrets`) via `Capability.Execute`. A client that legitimately batches exactly `MaxBatchSize` secret-get requests (an allowed, in-bound size) is always wrongfully denied service, forcing callers to either split requests unnecessarily or fail entirely when relying on the documented maximum. It does not itself cause fund loss, authentication bypass, or secret disclosure, but it is a genuine correctness/availability bug matching the reported bug class (boundary-condition off-by-one causing legitimate max-size operations to fail).

### Likelihood Explanation
High likelihood of being triggered: any caller that batches secrets requests up to the documented maximum (a natural thing to do to minimize request overhead) will deterministically hit this rejection every time, with no attacker action required — it's a straightforward, always-reproducible boundary bug.

### Recommendation
Change the comparison to be consistent with the rest of the batch-size validators:
```go
if len(request.Requests) > vaulttypes.MaxBatchSize {
    return fmt.Errorf("request batch size exceeds maximum of %d", vaulttypes.MaxBatchSize)
}
```
Alternatively, refactor `ValidateGetSecretsRequest` to reuse `MaxRequestBatchSizeLimiter.Check` like `validateWriteRequest`/`ValidateDeleteSecretsRequest` do, for consistency.

### Proof of Concept
1. Construct a `vaultcommon.GetSecretsRequest` with exactly `vaulttypes.MaxBatchSize` (a legitimate, in-bound size) `SecretRequest` entries.
2. Call `Capability.Execute` with `Method: vault.MethodGetSecrets` (as exercised by `TestCapability_Execute_GetSecretsRequestValidationFailed`, which already builds `reqs := make([]*vault.SecretRequest, vaulttypes.MaxBatchSize)`).
3. Observe the request is rejected with `"request batch size exceeds maximum of %d"` even though the batch size does not exceed the maximum, confirming the wrongful failure. [6](#0-5)

### Citations

**File:** core/capabilities/vault/validator.go (L180-186)
```go
func (r *RequestValidator) ValidateGetSecretsRequest(ctx context.Context, request *vaultcommon.GetSecretsRequest) error {
	if len(request.Requests) == 0 {
		return errors.New("no GetSecret request specified in request")
	}
	if len(request.Requests) >= vaulttypes.MaxBatchSize {
		return fmt.Errorf("request batch size exceeds maximum of %d", vaulttypes.MaxBatchSize)
	}
```

**File:** core/capabilities/vault/capability_test.go (L255-285)
```go
	t.Run("rejects batch when request count reaches MaxBatchSize", func(t *testing.T) {
		capability := newCapability(t)
		reqs := make([]*vault.SecretRequest, vaulttypes.MaxBatchSize)
		for i := range reqs {
			reqs[i] = &vault.SecretRequest{
				Id: &vault.SecretIdentifier{
					Key:       fmt.Sprintf("key%d", i),
					Namespace: "Bar",
					Owner:     workflowOwner,
				},
				EncryptionKeys: []string{"k"},
			}
		}
		gsr := &vault.GetSecretsRequest{Requests: reqs}
		anyproto, err := anypb.New(gsr)
		require.NoError(t, err)

		_, err = capability.Execute(t.Context(), capabilities.CapabilityRequest{
			Payload: anyproto,
			Method:  vault.MethodGetSecrets,
			Metadata: capabilities.RequestMetadata{
				WorkflowOwner:       workflowOwner,
				WorkflowID:          workflowID,
				WorkflowExecutionID: execID,
				ReferenceID:         refID,
			},
		})
		require.Error(t, err)
		require.ErrorContains(t, err, "could not validate get secrets request")
		require.ErrorContains(t, err, "request batch size exceeds maximum of")
	})
```

**File:** core/capabilities/vault/validator_test.go (L286-296)
```go
			name: "create accepts ciphertext at the limit",
			call: func(t *testing.T, validator *RequestValidator, value string) error {
				return validator.ValidateCreateSecretsRequest(t.Context(), nil, &vaultcommon.CreateSecretsRequest{
					RequestId: "request-id",
					EncryptedSecrets: []*vaultcommon.EncryptedSecret{
						{Id: id, EncryptedValue: value},
					},
				}, false)
			},
			value: hex.EncodeToString(make([]byte, 10)),
		},
```

**File:** core/capabilities/vault/limiter_helpers_test.go (L22-28)
```go
func (o *ownerOverrideLimiter) Check(ctx context.Context, n pkgconfig.Size) error {
	bound := o.boundFor(ctx)
	if n > bound {
		return limits.ErrorBoundLimited[pkgconfig.Size]{Limit: bound, Amount: n}
	}
	return nil
}
```
