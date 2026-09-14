### Title
Password Disclosure via URL Query Parameters in ETH/CSA/OCR/OCR2/P2P/VRF Key Import/Export Endpoints - (File: core/web/eth_keys_controller.go)

### Summary
Chainlink's node key-management REST API accepts the keystore encryption password (`oldpassword` on import, `newpassword` on export) as an HTTP **query string parameter** rather than in the request body/header, for every key type controller (`eth_keys_controller.go`, `csa_keys_controller.go`, `keys_controller.go`, `ocr_keys_controller.go`, `ocr2_keys_controller.go`, `p2p_keys_controller.go`, `vrf_keys_controller.go`). This is the same bug class as CVE-2018-20243 (Fineract exposing credentials via URL parameters on POST requests).

### Finding Description
`ETHKeysController.Import` reads the decryption password directly from the query string: [1](#0-0) 

and `ETHKeysController.Export` reads the new encryption password the same way: [2](#0-1) 

The CLI client itself builds these requests by embedding the password into the URL's query component before issuing the POST: [3](#0-2) 

The identical pattern (`oldpassword`/`newpassword` as query params) recurs across the other key type controllers and CLI commands, per the grep results across `core/cmd/keys_commands.go`, `core/cmd/ocr2_keys_commands.go`, `core/cmd/ocr_keys_commands.go`, `core/cmd/p2p_keys_commands.go`, `core/cmd/vrf_keys_commands.go`, `core/cmd/csa_keys_commands.go`, and their matching `core/web/*_controller.go` files.

Because these are full URLs (not just bodies), the plaintext password used to encrypt/decrypt a node's private key material is placed in a location that is routinely captured by infrastructure outside the application's own authentication/authorization boundary: HTTP access logs (nginx/ALB/reverse proxies), browser history if invoked from a browser-based tool, `Referer` headers if the request is ever proxied through another page, and general server request logging middleware.

### Impact Explanation
This differs from the pure Fineract case in one respect: the endpoints require prior authentication (an admin-role session or API token), so this is not by itself an unauthenticated-access issue. However, the impact is still concrete secret disclosure: the plaintext password protecting exported/imported Ethereum (and other) key material ends up in ancillary logging/telemetry systems that are typically accessible to a broader, lower-privileged audience (log aggregators, ops staff, reverse-proxy operators) than the set of users who hold node-admin credentials. If that password is reused (a common operational practice for keystore export passwords) or if the exported keyfile is also later exposed, an actor with only log access — not node API credentials — can decrypt the private key and gain full custody of the node's on-chain funds/identity. This matches the "key/secret disclosure" category called out in the validation rules.

### Likelihood Explanation
Likelihood is moderate. It requires an admin-authorized actor to actually invoke the import/export endpoints (a documented, expected operational action, e.g. key rotation or backup), and it requires some downstream component (log pipeline, proxy, monitoring) to be capturing full request URLs including query strings — which is default/common behavior in most deployments (access logs, APM/tracing, CDN/proxy logs). No exploitation of a bug in authentication logic is needed; the exposure occurs as a natural side effect of normal, legitimate use of the documented CLI/API.

### Recommendation
Move `oldpassword`/`newpassword` (and equivalents for CSA/OCR/OCR2/P2P/VRF key controllers) out of the URL query string and into the request body (already used for the keystore JSON payload) or a dedicated header, and update the corresponding CLI commands (`core/cmd/*_keys_commands.go`) to stop constructing `url.Values` with the password. Additionally, ensure any HTTP access-logging middleware in `core/web/router.go`/`core/web/middleware.go` redacts query strings for these routes as a defense-in-depth measure.

### Proof of Concept
1. As an authenticated node admin, run `chainlink keys eth import <file> --old-password=<pwfile>`.
2. Observe the underlying HTTP request constructed in `ImportETHKey` (`core/cmd/eth_keys_commands.go:281-293`): `POST /v2/keys/evm/import?oldpassword=<PLAINTEXT_PASSWORD>&evmChainID=...`.
3. Any component that logs the request line/URL (reverse proxy access log, APM tool, `gin` request logger if enabled) now contains the plaintext keystore password in cleartext, retrievable by anyone with read access to those logs even without node API credentials.

### Citations

**File:** core/web/eth_keys_controller.go (L202-222)
```go
func (ekc *ETHKeysController) Import(c *gin.Context) {
	ethKeyStore := ekc.app.GetKeyStore().Eth()
	defer ekc.app.GetLogger().ErrorIfFn(c.Request.Body.Close, "Error closing Import request body")

	bytes, err := io.ReadAll(c.Request.Body)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
	oldPassword := c.Query("oldpassword")
	cid := c.Query("evmChainID")
	chain, ok := ekc.getChain(c, cid)
	if !ok {
		return
	}

	key, err := ethKeyStore.Import(c.Request.Context(), bytes, oldPassword, chain.ID())
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
```

**File:** core/web/eth_keys_controller.go (L240-257)
```go
func (ekc *ETHKeysController) Export(c *gin.Context) {
	defer ekc.app.GetLogger().ErrorIfFn(c.Request.Body.Close, "Error closing Export request body")

	id := c.Param("address")
	newPassword := c.Query("newpassword")

	bytes, err := ekc.app.GetKeyStore().Eth().Export(c.Request.Context(), id, newPassword)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	ekc.app.GetAuditLogger().Audit(audit.KeyExported, map[string]any{
		"type": "ethereum",
		"id":   id,
	})

	c.Data(http.StatusOK, MediaType, bytes)
```

**File:** core/cmd/eth_keys_commands.go (L281-293)
```go
	importURL := url.URL{
		Path: "/v2/keys/evm/import",
	}
	query := importURL.Query()

	query.Set("oldpassword", strings.TrimSpace(string(oldPassword)))

	if c.IsSet("evmChainID") {
		query.Set("evmChainID", c.String("evmChainID"))
	}

	importURL.RawQuery = query.Encode()
	resp, err := s.HTTP.Post(s.ctx(), importURL.String(), bytes.NewReader(keyJSON))
```
