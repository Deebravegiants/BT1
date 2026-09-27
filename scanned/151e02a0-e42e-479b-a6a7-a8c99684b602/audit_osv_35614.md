# [C] Native CA trust persist

## Summary
Severity: Critical
Advisory: CVE-2026-11564
Aliases: CURL-CVE-2026-11564
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-11564
Type: osv

## Details
libcurl keeps previously used connections in a connection pool for subsequent
transfers to reuse if one of them matches the setup.

An easy handle that first uses default native CA trust can continue trusting
the native platform store after the application switches that same handle to
custom CA material for a later transfer.

## References
- https://curl.se/docs/CVE-2026-11564.html
- https://curl.se/docs/CVE-2026-11564.json
- https://hackerone.com/reports/3788984
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11564.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11564
