# [M] CVE-2023-23915

## Summary
Severity: Medium
Advisory: CVE-2023-23915
Aliases: CURL-CVE-2023-23915
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-02-23
Source: https://osv.dev/vulnerability/CVE-2023-23915
Type: osv

## Details
A cleartext transmission of sensitive information vulnerability exists in curl <v7.88.0 that could cause HSTS functionality to behave incorrectly when multiple URLs are requested in parallel. Using its HSTS support, curl can be instructed to use HTTPS instead of using an insecure clear-text HTTP step even when HTTP is provided in the URL. This HSTS mechanism would however surprisingly fail when multiple transfers are done in parallel as the HSTS cache file gets overwritten by the most recentlycompleted transfer. A later HTTP-only transfer to the earlier host name would then *not* get upgraded properly to HSTS.

## References
- https://hackerone.com/reports/1826048
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23915.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23915
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230309-0006/
