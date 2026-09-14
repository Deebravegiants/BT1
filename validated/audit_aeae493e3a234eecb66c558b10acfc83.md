### Title
Missing role check on `GET /v2/external_initiators` exposes `OutgoingToken` credentials to any authenticated (non-admin/edit) user - (File: core/web/router.go)

### Summary
The route wiring for the External Initiators API applies role restrictions (`auth.RequiresEditRole`) to `Create` and `Destroy`, but the `Index` (list) endpoint is registered with no role check at all, unlike every other sensitive collection endpoint in the same router block.

### Finding Description
In `v2Routes`, the external initiator routes are defined as: [1](#0-0) 

Note that `GET /v2/external_initiators` (`eia.Index`) is wrapped only with `paginatedRequest`, while `POST` and `DELETE` are wrapped with `auth.RequiresEditRole`. This means any user who can pass the outer `authv2` group's authentication (`AuthenticateByToken` or `AuthenticateBySession`) — including a low-privilege `view`-role user, or even a `run`-role identity minted via `AuthenticateExternalInitiator` — can call `Index` and enumerate every external initiator record.

The `Index` handler returns `presenters.ExternalInitiatorResource`, which includes `OutgoingToken`: [2](#0-1) 

`OutgoingToken`/`OutgoingSecret` are secrets generated at creation time (`utils.NewSecret(utils.DefaultSecretSize)`) specifically for the node to authenticate itself when calling out to the initiator's webhook: [3](#0-2) 

Because `Index` has no role gate, this design intent (role-gated write access via `RequiresEditRole`) is inconsistently applied to read access of a secret-bearing resource, unlike other resources such as `bridge_types` where `Index` (which does not expose secrets) is likewise open but no secret is embedded in its resource. Here the resource embeds outgoing credentials, so the missing role check on `Index` is a meaningful confidentiality gap: it lets any authenticated principal with the weakest role (`view`, or the automatically-assigned `run` role from `AuthenticateExternalInitiator`) read outgoing webhook secrets belonging to all external initiators registered on the node, regardless of whether that principal created them.

### Impact Explanation
Exposure of `OutgoingToken`/`OutgoingSecret` allows a low-privileged authenticated caller to impersonate the Chainlink node to any external initiator webhook that trusts those outgoing credentials, or to use the leaked token to interact with the initiator's external system as if it were the node. This is a credential-disclosure / authorization-bypass issue analogous to an "account compromise" class bug: a lower-trust identity can read the same operational secrets that only edit/admin-level identities are supposed to control, mirroring the underlying "unprivileged/compromised identity gains access to privileged secrets" theme of the referenced incident report.

### Likelihood Explanation
Likelihood is moderate: it requires External Initiators to be enabled (`JobPipeline().ExternalInitiatorsEnabled()`), at least one external initiator to have been registered, and an attacker to hold any valid authenticated credential on the node (session cookie, API token, or an external-initiator identity, since `AuthenticateExternalInitiator` auto-assigns the `run` role and the `authv2` group accepts token/session auth broadly). No admin/edit privilege is needed to trigger the disclosure — only the ability to authenticate at all.

### Recommendation
Wrap `authv2.GET("/external_initiators", ...)` with the same role guard used for `Create`/`Destroy` (`auth.RequiresEditRole`), or otherwise strip `OutgoingToken`/`OutgoingSecret` from the `Index`/list resource so that non-privileged authenticated users cannot read outgoing webhook credentials.

### Proof of Concept
1. Enable external initiators (`JobPipeline.ExternalInitiatorsEnabled = true`).
2. As an admin, create an external initiator via `POST /v2/external_initiators`, which returns and persists `OutgoingToken`/`OutgoingSecret` on the record (see `core/web/external_initiators_controller.go` `Create`).
3. Authenticate as a low-privilege user (e.g., a `view`-role session/API token, or via `AuthenticateExternalInitiator` which is auto-granted `UserRoleRun`) — see `core/web/auth/auth.go:119-148`.
4. Call `GET /v2/external_initiators` with that identity. Because the route registration has no `RequiresEditRole`/`RequiresAdminRole` wrapper (`core/web/router.go:264`), the request succeeds and the response includes each initiator's `OutgoingToken` field (`core/web/presenters/external_initiators.go:57-76`), disclosing the outbound webhook secret to a principal that should not have write/admin access to this resource.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/presenters/external_initiators.go (L57-76)
```go
type ExternalInitiatorResource struct {
	JAID
	Name          string         `json:"name"`
	URL           *models.WebURL `json:"url"`
	AccessKey     string         `json:"accessKey"`
	OutgoingToken string         `json:"outgoingToken"`
	CreatedAt     time.Time      `json:"createdAt"`
	UpdatedAt     time.Time      `json:"updatedAt"`
}

func NewExternalInitiatorResource(ei bridges.ExternalInitiator) ExternalInitiatorResource {
	return ExternalInitiatorResource{
		JAID:          NewJAID(strconv.FormatInt(ei.ID, 10)),
		Name:          ei.Name,
		URL:           ei.URL,
		AccessKey:     ei.AccessKey,
		OutgoingToken: ei.OutgoingToken,
		CreatedAt:     ei.CreatedAt,
		UpdatedAt:     ei.UpdatedAt,
	}
```

**File:** core/bridges/external_initiator.go (L38-57)
```go
func NewExternalInitiator(
	eia *auth.Token,
	eir *ExternalInitiatorRequest,
) (*ExternalInitiator, error) {
	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(eia, salt)
	if err != nil {
		return nil, pkgerrors.Wrap(err, "error hashing secret for external initiator")
	}

	return &ExternalInitiator{
		Name:           strings.ToLower(eir.Name),
		URL:            eir.URL,
		AccessKey:      eia.AccessKey,
		HashedSecret:   hashedSecret,
		Salt:           salt,
		OutgoingToken:  utils.NewSecret(utils.DefaultSecretSize),
		OutgoingSecret: utils.NewSecret(utils.DefaultSecretSize),
	}, nil
}
```
