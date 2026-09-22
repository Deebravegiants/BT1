# [M] QUIC certificate check bypass with wolfSSL

## Summary
Severity: Medium
Advisory: CVE-2024-2379
Aliases: CURL-CVE-2024-2379
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2024-2379
Type: osv

## Details
libcurl skips the certificate verification for a QUIC connection under certain conditions, when built to use wolfSSL. If told to use an unknown/bad cipher or curve, the error path accidentally skips the verification and returns OK, thus ignoring any certificate problems.

## References
- http://seclists.org/fulldisclosure/2024/Jul/18
- http://seclists.org/fulldisclosure/2024/Jul/19
- http://seclists.org/fulldisclosure/2024/Jul/20
- http://www.openwall.com/lists/oss-security/2024/03/27/2
- https://curl.se/docs/CVE-2024-2379.html
- https://curl.se/docs/CVE-2024-2379.json
- https://hackerone.com/reports/2410774
- https://support.apple.com/kb/HT214118
- https://support.apple.com/kb/HT214119
- https://support.apple.com/kb/HT214120
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2379.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2379
- https://security.netapp.com/advisory/ntap-20240531-0001/
