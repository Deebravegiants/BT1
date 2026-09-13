# [H] eventfd double close

## Summary
Severity: High
Advisory: CVE-2025-0665
Aliases: CURL-CVE-2025-0665
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-02-05
Source: https://osv.dev/vulnerability/CVE-2025-0665
Type: osv

## Details
libcurl would wrongly close the same eventfd file descriptor twice when taking
down a connection channel after having completed a threaded name resolve.

## References
- http://www.openwall.com/lists/oss-security/2025/02/05/2
- http://www.openwall.com/lists/oss-security/2025/02/05/5
- https://curl.se/docs/CVE-2025-0665.html
- https://curl.se/docs/CVE-2025-0665.json
- https://hackerone.com/reports/2954286
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0665.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0665
- https://security.netapp.com/advisory/ntap-20250306-0007/
