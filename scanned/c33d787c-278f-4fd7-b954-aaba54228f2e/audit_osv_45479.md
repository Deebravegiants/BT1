# [C] A flaw in curl’s cookie parsing logic allows a malicious HTTP server to set 'super cookies' that...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1213
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1213
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.21.0+0

## Details
A flaw in curl’s cookie parsing logic allows a malicious HTTP server to set
'super cookies' that bypass the Public Suffix List check. This enables an
attacker-controlled origin to inject cookies that curl subsequently scopes and
transmits to unrelated third-party domains.

## References
- https://curl.se/docs/CVE-2026-8924.html
- https://curl.se/docs/CVE-2026-8924.json
- https://github.com/advisories/GHSA-hm6c-rc5h-32m9
- https://hackerone.com/reports/3733905
- https://nvd.nist.gov/vuln/detail/CVE-2026-8924
