# [M] Nightingale < 9.0.0-beta.2 - Datasource Credential Disclosure to Low-Privilege Users

## Summary
Severity: Medium
Advisory: CVE-2026-58167
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58167
Type: osv

## Details
Nightingale (n9e) before 9.0.0-beta.2 exposes full datasource configurations, including plaintext database passwords, HTTP bearer tokens, HTTP basic-auth passwords, and mTLS client keys, to any authenticated low-privilege (Standard role) user through POST /api/n9e/datasource/list. The route is registered without an admin authorization gate, unlike the sibling datasource mutation routes, and the open-source DatasourceFilter does not redact secret fields, so the secret-bearing settings, http, and auth objects are serialized in the response. The disclosed credentials enable access to the connected downstream systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58167.json
- https://github.com/ccfos/nightingale/releases/tag/v9.0.0-beta.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-58167
- https://www.vulncheck.com/advisories/nightingale-beta-2-datasource-credential-disclosure-to-low-privilege-users
- https://github.com/ccfos/nightingale/pull/3175
- https://github.com/ccfos/nightingale/commit/762819fbaa2350b73bce45bfaf6f8cf74b4abef8
- https://github.com/ccfos/nightingale
- https://github.com/ccfos/nightingale/issues/3173
