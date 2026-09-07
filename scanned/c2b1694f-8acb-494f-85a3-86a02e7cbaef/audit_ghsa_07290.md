# [C] Gitea: Incomplete SSRF Protection in Webhook and Migration Allow-list Default Filter

## Summary
Severity: Critical
Advisory: GHSA-2r5c-gw76-rh3w
CVE: CVE-2026-22874
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-2r5c-gw76-rh3w
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.3

## Details
## Summary

Gitea's default SSRF allow-list ([`MatchBuiltinExternal`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/modules/hostmatcher/hostmatcher.go#L26-L27), used by both webhook delivery and repository migrations) relies on Go's standard library [`net.IP.IsPrivate()`](https://pkg.go.dev/net#IP.IsPrivate), which only covers RFC 1918 and RFC 4193. As a result, several IP ranges commonly used for cloud metadata services, internal networks, and IPv6 transition mechanisms are not blocked, allowing authenticated users to send HTTP requests to those destinations and read the responses via the webhook history UI.

## Details

The vulnerability lives in [`HostMatchList.checkIP`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/modules/hostmatcher/hostmatcher.go#L96-L114), specifically [line 103](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/modules/hostmatcher/hostmatcher.go#L103):

```go
case MatchBuiltinExternal:
    if ip.IsGlobalUnicast() && !ip.IsPrivate() {
        return true
    }
```

`net.IP.IsPrivate()` recognises only:
- `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (RFC 1918)
- `fc00::/7` (RFC 4193 IPv6 ULA)

It does **not** recognise:

| Range | Description |
|---|---|
| `100.64.0.0/10` | RFC 6598 Carrier-Grade NAT |
| `168.63.129.16/32` | Azure WireServer metadata endpoint |
| `172.32.0.0/11` | Non-RFC1918 portion of `172.0.0.0/8` (real-world internal use) |
| `64:ff9b::/96` | RFC 6052 IPv6 NAT64 (can embed `169.254.169.254`) |
| `2001::/32` | RFC 4380 Teredo tunneling |
| `2002::/16` | RFC 3056 6to4 |
| `2001:db8::/32` | RFC 3849 documentation |

The default is reached by webhook delivery at [`services/webhook/deliver.go#L312-L316`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/services/webhook/deliver.go#L312-L316) and by repository migrations at [`services/migrations/migrate.go#L522`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/services/migrations/migrate.go#L522).

The SSRF is **not blind**. Webhook delivery captures the response status, headers, and up to 1 MiB of body ([`services/webhook/deliver.go#L259-L270`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/services/webhook/deliver.go#L259-L270)) and renders them in the webhook history UI ([`templates/repo/settings/webhook/history.tmpl#L75-L85`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/templates/repo/settings/webhook/history.tmpl#L75-L85)), so attackers can read everything the targeted internal service returns.

## Impact

An authenticated user who can create or modify a webhook can:

- Reach cloud metadata endpoints (AWS IMDS via NAT64 `64:ff9b::a9fe:a9fe`, Azure WireServer `168.63.129.16`)
- Probe and exfiltrate from internal services on CGNAT (`100.64.0.0/10`) or non-RFC1918 172.x ranges
- Read full HTTP response bodies through the webhook history UI

The same default is applied to repository migrations, broadening the attack surface to users who can trigger a migration.

## Proof of Concept

The attached patch ([`gitea_ssrf_test.patch`](#patch)) adds [`TestSSRFBypassRanges`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/modules/hostmatcher/hostmatcher_test.go) to the existing test file. It uses [Go subtests](https://go.dev/blog/subtests) so each vulnerable range is its own named failing test case.

Run with:
```
go test -v ./modules/hostmatcher -run TestSSRFBypassRanges
```

Expected result on `4c37f4dacbac022f7beca75272439331f0368830`:
- **8 PASS** — RFC 1918, IPv6 private ranges, and legitimate public IPs (control cases)
- **10 FAIL** — Each failing subtest is a documented SSRF bypass

Sample failure output:
```
--- FAIL: TestSSRFBypassRanges/CGNAT_100.64.0.0/10_(RFC_6598)
    Error: Not equal: expected: false, actual: true
    Messages: ip=100.64.0.1
--- FAIL: TestSSRFBypassRanges/Azure_WireServer_168.63.129.16
    Error: Not equal: expected: false, actual: true
    Messages: ip=168.63.129.16
--- FAIL: TestSSRFBypassRanges/IPv6_NAT64_embedded_AWS_IMDS_169.254.169.254
    Error: Not equal: expected: false, actual: true
    Messages: ip=64:ff9b::a9fe:a9fe
```

## Suggested Remediation

I'd suggest treating the design of [`MatchBuiltinExternal`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/modules/hostmatcher/hostmatcher.go#L96-L114) as the bug — `IsPrivate()` is too narrow a definition of "internal." A comprehensive deny-list approach is what's needed here. For reference, CC-Tweaked's [`AddressPredicate.PrivatePattern`](https://github.com/cc-tweaked/CC-Tweaked/blob/3e7ce15ba6d5ab030092850f7e49829b64ba3555/projects/core/src/main/java/dan200/computercraft/core/apis/http/options/AddressPredicate.java#L116-L169) is a good reference list, blocking each of the ranges named in the table above plus a few others (multicast, broadcast, TEST-NET, etc.).

The exact remediation is at your discretion. 

## References

- Vulnerable function: [`modules/hostmatcher/hostmatcher.go#L96-L114`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/modules/hostmatcher/hostmatcher.go#L96-L114)
- Default for webhooks: [`services/webhook/deliver.go#L312-L316`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/services/webhook/deliver.go#L312-L316)
- Default for migrations: [`services/migrations/migrate.go#L522`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/services/migrations/migrate.go#L522)
- Response captured: [`services/webhook/deliver.go#L259-L270`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/services/webhook/deliver.go#L259-L270)
- Response rendered: [`templates/repo/settings/webhook/history.tmpl#L75-L85`](https://github.com/go-gitea/gitea/blob/4c37f4dacbac022f7beca75272439331f0368830/templates/repo/settings/webhook/history.tmpl#L75-L85)
- Go stdlib `net.IP.IsPrivate()`: <https://pkg.go.dev/net#IP.IsPrivate>
- CC-Tweaked reference deny-list: [`AddressPredicate.java#L116-L169`](https://github.com/cc-tweaked/CC-Tweaked/blob/3e7ce15ba6d5ab030092850f7e49829b64ba3555/projects/core/src/main/java/dan200/computercraft/core/apis/http/options/AddressPredicate.java#L116-L169)
- Go subtests pattern: <https://go.dev/blog/subtests>
- RFC 6598 (CGNAT), RFC 6052 (NAT64), RFC 4380 (Teredo), RFC 3056 (6to4), RFC 3849 (documentation)

---

## Patch <a name="patch"></a>

Proposed `gitea_ssrf_test.patch`:

```diff
diff --git a/modules/hostmatcher/hostmatcher_test.go b/modules/hostmatcher/hostmatcher_test.go
index c781847..0b39e60 100644
--- a/modules/hostmatcher/hostmatcher_test.go
+++ b/modules/hostmatcher/hostmatcher_test.go
@@ -159,3 +159,56 @@ func TestHostOrIPMatchesList(t *testing.T) {
 	}
 	test(cases)
 }
+
+// TestSSRFBypassRanges verifies that the "external" filter (the default used by
+// webhook delivery and repository migrations) blocks dangerous IP ranges.
+//
+// Each subtest's `allowed` field is the expected return value of MatchHostOrIP:
+//   - false: the IP should be blocked (rejected by the filter)
+//   - true:  the IP should be allowed (a legitimate public destination)
+//
+// Subtests that FAIL are documented SSRF bypasses: IP ranges that should be
+// blocked but are incorrectly allowed because the underlying check relies on
+// net.IP.IsPrivate(), which only covers RFC 1918 and RFC 4193.
+func TestSSRFBypassRanges(t *testing.T) {
+	type tc struct {
+		ip      net.IP
+		allowed bool
+	}
+
+	hl := ParseHostMatchList("", "external")
+
+	cases := map[string]tc{
+		// RFC 1918 / IPv6 private ranges - correctly blocked
+		"RFC1918 10.0.0.0/8":        {net.ParseIP("10.0.0.1"), false},
+		"RFC1918 172.16.0.0/12":     {net.ParseIP("172.16.0.1"), false},
+		"RFC1918 192.168.0.0/16":    {net.ParseIP("192.168.1.1"), false},
+		"IPv6 loopback ::1":         {net.ParseIP("::1"), false},
+		"IPv6 link-local fe80::/10": {net.ParseIP("fe80::1"), false},
+		"IPv6 ULA fd00::/8":         {net.ParseIP("fd00::1"), false},
+
+		// Legitimate public IPs - correctly allowed
+		"Public IPv4 (Google DNS)": {net.ParseIP("8.8.8.8"), true},
+		"Public IPv6 (Google DNS)": {net.ParseIP("2001:4860:4860::8888"), true},
+
+		// SSRF bypasses - the assertions below intentionally describe the
+		// expected secure behavior (allowed=false). Each failing subtest is
+		// a documented bypass.
+		"CGNAT 100.64.0.0/10 (RFC 6598)":              {net.ParseIP("100.64.0.1"), false},
+		"CGNAT 100.127.255.254 (RFC 6598)":            {net.ParseIP("100.127.255.254"), false},
+		"Azure WireServer 168.63.129.16":              {net.ParseIP("168.63.129.16"), false},
+		"Non-RFC1918 172.32.0.0/11":                   {net.ParseIP("172.32.0.1"), false},
+		"Non-RFC1918 172.45.0.0/16":                   {net.ParseIP("172.45.0.1"), false},
+		"IPv6 NAT64 64:ff9b::/96 (RFC 6052)":          {net.ParseIP("64:ff9b::1"), false},
+		"IPv6 NAT64 embedded AWS IMDS 169.254.169.254": {net.ParseIP("64:ff9b::a9fe:a9fe"), false},
+		"IPv6 Teredo 2001::/32 (RFC 4380)":            {net.ParseIP("2001::1"), false},
+		"IPv6 6to4 2002::/16 (RFC 3056)":              {net.ParseIP("2002::1"), false},
+		"IPv6 documentation 2001:db8::/32 (RFC 3849)": {net.ParseIP("2001:db8::1"), false},
+	}
+
+	for name, c := range cases {
+		t.Run(name, func(t *testing.T) {
+			assert.Equalf(t, c.allowed, hl.MatchHostOrIP("", c.ip), "ip=%v", c.ip)
+		})
+	}
+}
```

## Credit

This vulnerability was uncovered by @JLLeitschuh of the @braze-inc security team.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-2r5c-gw76-rh3w
- https://nvd.nist.gov/vuln/detail/CVE-2026-22874
- https://github.com/go-gitea/gitea/pull/38059
- https://github.com/go-gitea/gitea/pull/38173
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.3
