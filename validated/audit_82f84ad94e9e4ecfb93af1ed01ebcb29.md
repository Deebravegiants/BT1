I found a valid analog. This maps directly to the report's bug class: a highly sensitive operation that should require the strictest role/quorum-equivalent gate is instead placed at a lower privilege tier than comparable sensitive operations in the same codebase.

### Title
`VaultController::ExportDKGResult` exposes raw DKG key-share material to Edit-role users instead of requiring Admin role - ([File: core/web/router.go])

### Summary
`/v2/vault/dkg_results/export` returns the raw hex-encoded DKG result package (containing encrypted-but-recoverable key-share material used to reconstruct the Vault DON's master private key material) to any authenticated user holding only the `Edit` role, while every other key-export endpoint in the same router (`ETH`, `OCR`, `OCR2`, `P2P`, `CSA`, `VRF`, Solana/Cosmos/Starknet/Aptos/Stellar/Tron/TON) is gated behind `RequiresAdminRole`.

### Finding Description
`core/web/router.go` wires the two Vault endpoints with only `RequiresEditRole`: [1](#0-0) 

Contrast this with every other credential-export route in the exact same function, all of which require `RequiresAdminRole`: [2](#0-1) [3](#0-2) [4](#0-3) 

`ExportDKGResult` reads the stored DKG result package and returns it hex-encoded directly in the JSON response: [5](#0-4) 

This DKG result package contains the encrypted private key shares (`report_with_result_package`) that, combined with the node's DKG recipient private key, allow reconstruction of the Vault DON's master private key share — the same class of secret material that ETH/OCR/OCR2/P2P/VRF exports protect with `RequiresAdminRole`. The role-check hierarchy in `core/web/auth/auth.go` treats `RequiresEditRole` as strictly weaker than `RequiresAdminRole`: [6](#0-5) 

This is the same bug class as the external report: a highly sensitive operation (key/secret export) was not included in the strictest privilege tier that the codebase's own established convention uses for comparable operations, making it reachable by a lower-privileged authenticated actor than intended.

### Impact Explanation
An API user provisioned with only the `Edit` role (a role explicitly intended to be less privileged than `Admin`, per the RBAC test matrix in `core/web/auth/auth_test.go`) can call `POST /v2/vault/dkg_results/export` and obtain the raw DKG result package for any known `instanceId`. This discloses key-share material that should only be accessible to node operators with full administrative trust, undermining the confidentiality guarantees of the Vault capability's key-management model. This is a concrete key/secret disclosure via a role bypass, matching the "Accept" criteria in the validation rules.

### Likelihood Explanation
Likelihood is high: exploitation requires nothing more than possessing valid Edit-role API credentials (a role routinely granted to less-trusted operators/automation) and knowing or guessing a valid `instanceId`. No additional privilege escalation or race condition is needed — the router itself grants access.

### Proof of Concept
1. Provision an API credential with role `Edit` (not `Admin`).
2. Authenticate and call:
```
POST /v2/vault/dkg_results/export
{"instanceId": "<known-instance-id>"}
```
3. The response returns `hexDKGResultPackage`, the raw DKG result package, as shown in `VaultController.ExportDKGResult` [7](#0-6) , confirming an Edit-role actor obtained key-share material intended for Admin-only access.

### Recommendation
Change the route registration in `core/web/router.go` to use `auth.RequiresAdminRole` for both `/vault/dkg_results/verify` and, at minimum, `/vault/dkg_results/export`, consistent with every other secret/key export endpoint in the router: [1](#0-0)

### Citations

**File:** core/web/router.go (L309-320)
```go
		csakc := CSAKeysController{app}
		authv2.GET("/keys/csa", csakc.Index)
		authv2.POST("/keys/csa", auth.RequiresEditRole(csakc.Create))
		authv2.POST("/keys/csa/import", auth.RequiresAdminRole(csakc.Import))
		authv2.POST("/keys/csa/export/:ID", auth.RequiresAdminRole(csakc.Export))

		ekc := NewETHKeysController(app)
		authv2.GET("/keys/eth", ekc.Index)
		authv2.POST("/keys/eth", auth.RequiresEditRole(ekc.Create))
		authv2.DELETE("/keys/eth/:keyID", auth.RequiresAdminRole(ekc.Delete))
		authv2.POST("/keys/eth/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/eth/export/:address", auth.RequiresAdminRole(ekc.Export))
```

**File:** core/web/router.go (L337-349)
```go
		ocrkc := OCRKeysController{app}
		authv2.GET("/keys/ocr", ocrkc.Index)
		authv2.POST("/keys/ocr", auth.RequiresEditRole(ocrkc.Create))
		authv2.DELETE("/keys/ocr/:keyID", auth.RequiresAdminRole(ocrkc.Delete))
		authv2.POST("/keys/ocr/import", auth.RequiresAdminRole(ocrkc.Import))
		authv2.POST("/keys/ocr/export/:ID", auth.RequiresAdminRole(ocrkc.Export))

		ocr2kc := OCR2KeysController{app}
		authv2.GET("/keys/ocr2", ocr2kc.Index)
		authv2.POST("/keys/ocr2/:chainType", auth.RequiresEditRole(ocr2kc.Create))
		authv2.DELETE("/keys/ocr2/:keyID", auth.RequiresAdminRole(ocr2kc.Delete))
		authv2.POST("/keys/ocr2/import", auth.RequiresAdminRole(ocr2kc.Import))
		authv2.POST("/keys/ocr2/export/:ID", auth.RequiresAdminRole(ocr2kc.Export))
```

**File:** core/web/router.go (L378-383)
```go
		vrfkc := VRFKeysController{app}
		authv2.GET("/keys/vrf", vrfkc.Index)
		authv2.POST("/keys/vrf", auth.RequiresEditRole(vrfkc.Create))
		authv2.DELETE("/keys/vrf/:keyID", auth.RequiresAdminRole(vrfkc.Delete))
		authv2.POST("/keys/vrf/import", auth.RequiresAdminRole(vrfkc.Import))
		authv2.POST("/keys/vrf/export/:keyID", auth.RequiresAdminRole(vrfkc.Export))
```

**File:** core/web/router.go (L441-443)
```go
		vault := VaultController{app}
		authv2.POST("/vault/dkg_results/verify", auth.RequiresEditRole(vault.VerifyDKGResult))
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))
```

**File:** core/web/vault_controller.go (L89-119)
```go
// ExportDKGResult returns the DKGResult corresponding to the given instance ID
// "POST <application>/vault/dkg_results/export"
func (vc *VaultController) ExportDKGResult(c *gin.Context) {
	var req ExportDKGResultRequest
	err := json.NewDecoder(c.Request.Body).Decode(&req)
	if err != nil {
		jsonAPIError(c, http.StatusBadRequest, errors.New("could not parse request body"))
		return
	}

	if req.InstanceID == "" {
		jsonAPIError(c, http.StatusBadRequest, errors.New("instanceId is required"))
		return
	}

	orm := vault.NewVaultORM(vc.App.GetDB())
	v, err := orm.ReadResultPackage(c.Request.Context(), dkgocrtypes.InstanceID(req.InstanceID))
	if err != nil {
		jsonAPIError(c, http.StatusNotFound, err)
		return
	}

	if v == nil {
		jsonAPIError(c, http.StatusNotFound, errors.New("DKG result not found"))
		return
	}

	hexPackage := hex.EncodeToString(v.ReportWithResultPackage)
	sha := sha256.Sum256(v.ReportWithResultPackage)
	shaStr := hex.EncodeToString(sha[:])
	jsonAPIResponse(c, presenters.NewExportDKGResultResource(hexPackage, shaStr), "exportDKGResult")
```

**File:** core/web/auth/auth.go (L217-253)
```go
// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```
