All claims in the report are directly verified in the code. `GET /v2/external_initiators` on line 264 of `core/web/router.go` is registered with no role wrapper, while `POST`/`DELETE` on the same resource use `auth.RequiresEditRole` [1](#0-0) . The RBAC test table explicitly documents this as intentional-per-test behavior, marking the index route accessible to view-only, run, and edit roles alike [2](#0-1) . `RequiresRunRole` blocks only `UserRoleView`, and since the index route has no such wrapper at all, a `UserRoleView` session passes straight through to the handler [3](#0-2) . The presenter `ExternalInitiatorResource` used by `Index` includes `AccessKey` and `OutgoingToken` for every initiator, unfiltered by requester/owner [4](#0-3) .

Audit Report

## Title
Unauthenticated-role disclosure of External Initiator credentials via `GET /v2/external_initiators` missing role-gate - (File: core/web/router.go)

## Summary
The `GET /v2/external_initiators` route in `core/web/router.go` is registered without any `auth.RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` wrapper, unlike its sibling `POST`/`DELETE` routes on the same resource which require `RequiresEditRole`. As a result, any authenticated user — including one provisioned with only the lowest-privileged `UserRoleView` — can call this endpoint and receive the `AccessKey` and `OutgoingToken` credentials for every External Initiator registered on the node, not just ones they created.

## Finding Description
`core/web/router.go` registers the External Initiator routes as:
```go
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```
Only the `authv2` group-level middleware (`auth.Authenticate` via session or API token) applies to `Index`; there is no per-role check. This is corroborated by the RBAC route table test, which marks `GET /v2/external_initiators` as `viewOnlyAllowed: true`. `RequiresRunRole` (the narrowest role gate available, requiring anything above `UserRoleView`) is not even applied here — the route has strictly weaker protection than every other credential-bearing resource in the router.

The `Index` handler serializes each initiator via `NewExternalInitiatorResource`, which copies `AccessKey` and `OutgoingToken` from the underlying `bridges.ExternalInitiator` model into the JSON response for every record returned by the paginated query, with no filtering by creator/owner. The integration test `TestExternalInitiatorsController_Index` confirms this: it asserts that `AccessKey` and `OutgoingToken` for initiators are present in the list response.

`AccessKey` is one half of the credential pair (`auth.Token`) used in `bridges.AuthenticateExternalInitiator` to authenticate incoming job-run trigger requests; disclosing it (even without the paired secret) reduces the attack surface for guessing/brute-forcing the corresponding secret and reveals which initiators exist and their identifiers. `OutgoingToken` is the token the Chainlink node itself sends to the external initiator's URL, so its disclosure could allow replay against that third-party endpoint if it treats the token as a bearer credential.

## Impact Explanation
This is a genuine authorization-boundary defect: a `UserRoleView` session — intended for read-only, non-sensitive dashboard access, and explicitly blocked from run/edit/admin routes elsewhere via `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` — can read credential material (`AccessKey`, `OutgoingToken`) belonging to External Initiators it did not create. This falls into the "key/secret exfiltration" and "node API authentication or role bypass" in-scope impact categories, since it discloses authentication tokens across a privilege boundary that the codebase clearly intends to enforce for every other credential-bearing resource (CSA/ETH/OCR/P2P/VRF keys all gate reads/writes behind Edit/Admin roles). Severity is bounded by the fact that only `AccessKey`/`OutgoingToken` are exposed — not `Secret`/`OutgoingSecret`, which remain visible only once at `Create` time via the separate `ExternalInitiatorAuthentication` presenter.

## Likelihood Explanation
Exploitation requires only a single authenticated `GET` request with a valid session or API token belonging to any role, including `UserRoleView`. `JobPipeline.ExternalInitiatorsEnabled` must be true and at least one External Initiator must exist, and the node must have provisioned at least one `UserRoleView` account (a documented, supported role for restricting access) — all realistic, supported node configurations. No special timing, race conditions, or admin cooperation beyond normal multi-user node administration is required.

## Recommendation
Wrap `GET /v2/external_initiators` with at least `auth.RequiresRunRole` (consistent with the minimal role needed elsewhere), or `auth.RequiresEditRole` to match `POST`/`DELETE` on the same resource. Additionally, consider removing `AccessKey`/`OutgoingToken` from `ExternalInitiatorResource` entirely, since these credentials are already surfaced once at creation time via `ExternalInitiatorAuthentication`, and the list/index view does not need to re-expose them.

## Proof of Concept
1. Set `JobPipeline.ExternalInitiatorsEnabled = true` on a local node.
2. As an `admin`/`edit` user, create an External Initiator: `POST /v2/external_initiators {"name":"foo"}`; note the server generates and stores an `AccessKey` and `OutgoingToken`.
3. Provision a second user/API token with role `UserRoleView`.
4. As the `UserRoleView` user, issue `GET /v2/external_initiators?size=50`.
5. Observe the JSON response body contains `accessKey` and `outgoingToken` fields for the initiator created in step 2 — reproducible directly via the existing integration test `TestExternalInitiatorsController_Index` in `core/web/external_initiators_controller_test.go`, which performs this exact request/assertion pattern, combined with the RBAC test table entry in `core/web/auth/auth_test.go` line 224 confirming no role restriction is enforced on this route.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/auth/auth_test.go (L224-226)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
```

**File:** core/web/auth/auth.go (L198-215)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
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
