# [C] trailing dot domain super cookie

## Summary
Severity: Critical
Advisory: CVE-2026-8924
Aliases: CURL-CVE-2026-8924
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-8924
Type: osv

## Details
A flaw in curl’s cookie parsing logic allows a malicious HTTP server to set
'super cookies' that bypass the Public Suffix List check. This enables an
attacker-controlled origin to inject cookies that curl subsequently scopes and
transmits to unrelated third-party domains.

## References
- https://curl.se/docs/CVE-2026-8924.html
- https://curl.se/docs/CVE-2026-8924.json
- https://hackerone.com/reports/3733905
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8924.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8924
