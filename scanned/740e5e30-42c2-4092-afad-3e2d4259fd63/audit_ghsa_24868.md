# [M] Cabot Cross Site Scripting (XSS) vulnerability via Address column

## Summary
Severity: Medium
Advisory: GHSA-8q2h-4mq6-396j
CVE: CVE-2020-25449
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8q2h-4mq6-396j
Type: github-advisory

## Affected
- PyPI: `cabot` — affected >=0

## Details
Cross Site Scripting (XSS) vulnerability in Arachnys Cabot up to and including 0.11.12 can be exploited via the Address column.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25449
- https://github.com/arachnys/cabot/commit/18708572cb0ed143842409419eada91160413973
- https://github.com/arachnys/cabot
- https://github.com/pypa/advisory-database/tree/main/vulns/cabot/PYSEC-2020-226.yaml
- https://itsmeanonartist.tech/blogs/blog2.html
- https://packetstormsecurity.com/files/159070/Cabot-0.11.12-Cross-Site-Scripting.html
- https://www.exploit-db.com/exploits/48791
- https://www.exploitalert.com/view-details.html?id=36106
