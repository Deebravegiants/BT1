Audit Report

## Title
Any authenticated user (including View-only role) can read External Initiator outgoing credentials via `GET /v2/external_initiators` - (File: core/web/router.go)

## Summary
The `/v2/external_initiators` `GET` listing route is registered in `core/web/router.go` without any role-gating middleware, while the sibling `POST`/`DELETE` routes are wrapped in `auth.RequiresEditRole`. As a result, any authenticated user — including the lowest-privilege `view` role — can call `ExternalInitiatorsController.Index` and receive every configured External Initiator's `AccessKey` and `OutgoingToken` in the JSON response.

## Finding Description
In `core/web/router.go`, the `authv2` group registers:
```go
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
``` [1](#0-0) 

Only `Create` and `Destroy` are wrapped with `auth.RequiresEditRole`; `Index` is reachable by any user passing only `auth.Authenticate`, i.e. `view` role and above. `ExternalInitiatorsController.Index` builds the full resource list with no redaction: [2](#0-1) 

`ExternalInitiatorResource` serializes `AccessKey` and `OutgoingToken` directly: [3](#0-2) 

This behavior is confirmed both by the controller test asserting `AccessKey`/`OutgoingToken` are present in the listed resources, and by the RBAC test table in `core/web/auth/auth_test.go` which documents `GET /v2/external_initiators` as `viewOnlyAllowed: true` while `POST`/`DELETE` on the same path require edit privileges — confirming this is the current, tested, but under-protected behavior of the route rather than a hypothetical scenario.

`AccessKey`/`OutgoingToken` are credential material: `AccessKey` (with its paired `Secret`) authenticates inbound calls from the external initiator into the node (`AuthenticateExternalInitiator`), and `OutgoingToken`/`OutgoingSecret` authenticate outbound node-to-initiator webhook calls. Exposing these to `view`-role users breaks the intended 4-tier role segregation (`view` < `run` < `edit` < `admin`) that gates `Create`/`Destroy` on this same resource at `edit`, and that gates comparable credential-export endpoints (e.g., key export) at `admin`.

## Impact Explanation
A `view`-role user, intended for read-only observation, can retrieve secret-equivalent `AccessKey`/`OutgoingToken` values for all configured External Initiators, enabling impersonation of the external-initiator relationship or forging/replaying authenticated calls that should require `edit`/`admin` privilege. This is a concrete privilege-escalation / secret-exfiltration bug within the node's own authorization model, not a leaked-credential or misconfiguration issue — the credentials are disclosed by the vulnerable code path itself to an already-authenticated, legitimately provisioned low-privilege user.

## Likelihood Explanation
Exploitation requires nothing beyond a single authenticated `GET /v2/external_initiators` request from any provisioned `view`-role API user or token — no race conditions, no additional access, and no admin/operator/host access is needed. This is trivially and repeatably reachable by design of the RBAC hierarchy that legitimately supports `view`-role accounts.

## Recommendation
Wrap the `Index` route with at least `auth.RequiresEditRole` to match `Create`/`Destroy`, or strip `AccessKey`/`OutgoingToken` from the resource returned by non-privileged roles, consistent with how other credential-bearing export endpoints are separated from list endpoints.

## Proof of Concept
1. Provision an API user with role `view` (`chainlink admin users create --role view`).
2. As an `edit`/`admin` user, create an External Initiator via `POST /v2/external_initiators {"name":"bitcoin","url":"https://example.com"}`.
3. Authenticate as the `view` user and call `GET /v2/external_initiators`.
4. Observe the JSON response includes `accessKey` and `outgoingToken` for the initiator, as validated by the existing test asserting `AccessKey`/`OutgoingToken` equality in the paginated response — confirmed reachable per the `viewOnlyAllowed: true` RBAC test entry for this exact route in `core/web/auth/auth_test.go`. [4](#0-3)

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/external_initiators_controller.go (L50-59)
```go
func (eic *ExternalInitiatorsController) Index(c *gin.Context, size, page, offset int) {
	ctx := c.Request.Context()
	externalInitiators, count, err := eic.App.BridgeORM().ExternalInitiators(ctx, offset, size)
	resources := make([]presenters.ExternalInitiatorResource, 0, len(externalInitiators))
	for _, initiator := range externalInitiators {
		resources = append(resources, presenters.NewExternalInitiatorResource(initiator))
	}

	paginatedResponse(c, "externalInitiators", size, page, resources, count, err)
}
```

**File:** core/web/presenters/external_initiators.go (L57-77)
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
}
```

**File:** core/web/auth/auth_test.go (L224-226)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
```
