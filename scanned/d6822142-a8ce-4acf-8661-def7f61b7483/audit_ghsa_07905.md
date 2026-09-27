# [H] Feathers exposes internal headers via unencrypted session cookie

## Summary
Severity: High
Advisory: GHSA-9m9c-vpv5-9g85
CVE: CVE-2026-27193
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-9m9c-vpv5-9g85
Type: github-advisory

## Affected
- npm: `@feathersjs/authentication-oauth` — affected >=0 <5.0.40

## Details
All HTTP request headers are stored in the session cookie, which is signed but not encrypted, exposing internal proxy/gateway headers to clients.

The OAuth service stores the complete headers object in the session:
```javascript
// https://github.com/feathersjs/feathers/blob/dove/packages/authentication-oauth/src/service.ts#L173
session.headers = headers;
```

The session is persisted using `cookie-session`, which base64-encodes the data. While the cookie is signed to prevent tampering, the contents are readable by anyone by simply decoding the base64 value.

Under specific deployment configurations (e.g., behind reverse proxies or API gateways), this can lead to exposure of sensitive internal infrastructure details such as API keys, service tokens, and internal IP addresses.

**Credits**:  Abdelwahed Madani Yousfi (@vvxhid) / Edoardo Geraci (@b0-n0-b0) / Thomas Rinsma (@ThomasRinsma) From Codean Labs.

## References
- https://github.com/feathersjs/feathers/security/advisories/GHSA-9m9c-vpv5-9g85
- https://nvd.nist.gov/vuln/detail/CVE-2026-27193
- https://github.com/feathersjs/feathers/commit/ee19a0ae9bc2ebf23b1fe598a1f7361981b65401
- https://github.com/feathersjs/feathers
- https://github.com/feathersjs/feathers/releases/tag/v5.0.40
