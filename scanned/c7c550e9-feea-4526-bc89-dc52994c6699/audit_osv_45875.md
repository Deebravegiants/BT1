# [M] When doing SSH-based transfers using either SCP or SFTP, and setting the `known_hosts` file, libcurl...

## Summary
Severity: Medium
Advisory: JLSEC-2026-430
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-430
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.18.0+0

## Details
When doing SSH-based transfers using either SCP or SFTP, and setting the
`known_hosts` file, libcurl could still mistakenly accept connecting to hosts
*not present* in the specified file if they were added as recognized in the
libssh *global* `known_hosts` file.

## References
- http://www.openwall.com/lists/oss-security/2026/01/07/6
- https://curl.se/docs/CVE-2025-15079.html
- https://curl.se/docs/CVE-2025-15079.json
- https://github.com/advisories/GHSA-7q9p-cx8r-rh2q
- https://hackerone.com/reports/3477116
- https://nvd.nist.gov/vuln/detail/CVE-2025-15079
