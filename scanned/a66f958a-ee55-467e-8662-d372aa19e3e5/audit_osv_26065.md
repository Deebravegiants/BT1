# [H] Bazarr Arbitrary file read in /api/swaggerui/static endpoint

## Summary
Severity: High
Advisory: CVE-2023-50265
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-15
Source: https://osv.dev/vulnerability/CVE-2023-50265
Type: osv

## Details
Bazarr manages and downloads subtitles. Prior to 1.3.1, the /api/swaggerui/static endpoint in bazarr/app/ui.py does not validate the user-controlled filename variable and uses it in the send_file function, which leads to an arbitrary file read on the system. This issue is fixed in version 1.3.1.

## References
- https://github.com/morpheus65535/bazarr/releases/tag/v1.3.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50265.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-50265
- https://securitylab.github.com/advisories/GHSL-2023-192_GHSL-2023-194_bazarr/
- https://github.com/morpheus65535/bazarr/commit/17add7fbb3ae1919a40d505470d499d46df9ae6b
