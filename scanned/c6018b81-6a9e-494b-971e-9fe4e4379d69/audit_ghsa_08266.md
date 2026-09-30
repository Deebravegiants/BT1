# [H] Parse Server: Pre-authentication denial of service via client version header regex backtracking

## Summary
Severity: High
Advisory: GHSA-38m6-82c8-4xfm
CVE: CVE-2026-47138
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-23
Source: https://github.com/advisories/GHSA-38m6-82c8-4xfm
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.9.1-alpha.1
- npm: `parse-server` — affected >=0 <8.6.77

## Details
### Impact

An unauthenticated attacker who knows a publicly-known Parse Application ID can submit a single HTTP request whose client SDK version field contains adversarial input that triggers polynomial backtracking in a request-header parser. The parsing runs before session authentication and before rate limiting on every `/parse/*` request, so the request consumes seconds to minutes of synchronous CPU on a Node.js worker before any access control evaluates it. A small number of concurrent requests can saturate a worker; a single large request via the body-field variant can pin a worker for minutes. Production deployments running the default configuration are affected.

### Patches

The client SDK version capture and parsing have been removed entirely. The Parse JS SDK compatibility table defines a strict version-pinned contract between Parse Server and the Parse JS SDK; server-side adaptation to client SDK version is an obsolete pattern that contradicts that contract. The vulnerable parser, the `clientSDK` parameter that threaded its output through routers, and the legacy code path it gated are all removed. The `X-Parse-Client-Version` header and `_ClientVersion` JSON body field are now silently ignored on every request; supported Parse SDKs are unaffected.

### Workarounds

Deploy a reverse proxy or WAF in front of Parse Server that strips or strictly size-limits the `X-Parse-Client-Version` header AND the `_ClientVersion` field in JSON request bodies on every `/parse/*` route before forwarding to the server. A header-size cap alone is insufficient: the body-field variant requires inspection of JSON content. Upgrading to the patched version is the recommended remediation.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-38m6-82c8-4xfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-47138
- https://github.com/parse-community/parse-server/pull/10463
- https://github.com/parse-community/parse-server/pull/10464
- https://github.com/parse-community/parse-server
