# [H] CVE-2026-38822

## Summary
Severity: High
Advisory: CVE-2026-38822
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-38822
Type: osv

## Details
In openNDS before 11.0.0, the client_params.sh script, invoked by the openNDS daemon to serve the authenticated client status page, is vulnerable to OS command injection through crafted HTTP GET query parameter keys. An authenticated captive portal user can inject arbitrary shell commands by embedding semicolons in a URL query parameter name.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38822.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38822
- https://github.com/openNDS/openNDS/commit/294983e859bb678eef7db06fc9f6afab0b489d8e
