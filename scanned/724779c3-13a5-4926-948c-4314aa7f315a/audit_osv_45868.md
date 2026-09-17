# [M] curl's code for managing SSH connections when SFTP was done using the wolfSSH powered backend was...

## Summary
Severity: Medium
Advisory: JLSEC-2026-424
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-424
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.17.0+0
- Julia: `LibCURL_jll` — affected >=7.70.0+0 <8.17.0+0

## Details
curl's code for managing SSH connections when SFTP was done using the wolfSSH
powered backend was flawed and missed host verification mechanisms.

This prevents curl from detecting MITM attackers and more.

## References
- http://www.openwall.com/lists/oss-security/2025/11/05/2
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://curl.se/docs/CVE-2025-10966.html
- https://curl.se/docs/CVE-2025-10966.json
- https://github.com/advisories/GHSA-5gff-h54g-38r2
- https://hackerone.com/reports/3355218
- https://nvd.nist.gov/vuln/detail/CVE-2025-10966
