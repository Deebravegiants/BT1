# [H] TinyWeb: Integer Overflow in `_Val` (HTTP Request Smuggling)

## Summary
Severity: High
Advisory: CVE-2026-28497
Aliases: GHSA-rp8j-cx7r-mw9f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28497
Type: osv

## Details
TinyWeb is a web server (HTTP, HTTPS) written in Delphi for Win32. Prior to version 2.03, an integer overflow vulnerability in the string-to-integer conversion routine (_Val) allows an unauthenticated remote attacker to bypass Content-Length restrictions and perform HTTP Request Smuggling. This can lead to unauthorized access, security filter bypass, and potential cache poisoning. The impact is critical for servers using persistent connections (Keep-Alive). This issue has been patched in version 2.03.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28497.json
- https://github.com/maximmasiutin/TinyWeb/security/advisories/GHSA-rp8j-cx7r-mw9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-28497
- https://github.com/maximmasiutin/TinyWeb/commit/d2edd0322c3d74beee0a6c0191299b8946695d4e
