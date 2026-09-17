# [M] EduSoho < 22.4.7 Arbitrary File Read via classroom-course-statistics

## Summary
Severity: Medium
Advisory: CVE-2023-7335
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2023-7335
Type: osv

## Details
EduSoho versions prior to 22.4.7 contain an arbitrary file read vulnerability in the classroom-course-statistics export functionality. A remote, unauthenticated attacker can supply crafted path traversal sequences in the fileNames[] parameter to read arbitrary files from the server filesystem, including application configuration files such as config/parameters.yml that may contain secrets and database credentials. Exploitation evidence was observed by the Shadowserver Foundation on 2026-01-19 (UTC).

## References
- https://www.edusoho.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7335.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7335
- https://www.cnvd.org.cn/flaw/show/CNVD-2023-03903
- https://www.vulncheck.com/advisories/edusoho-arbitrary-file-read-via-classroom-course-statistics
- https://github.com/edusoho/edusoho/releases/tag/v22.4.7
- https://github.com/edusoho/edusoho
- https://blog.csdn.net/qq_41904294/article/details/135007351
- https://cn-sec.com/archives/2451582.html
- https://github.com/gobysec/GobyVuls/blob/master/CNVD-2023-03903.md
- https://github.com/zeroChen00/exp-poc/blob/main/EduSoho%E6%95%99%E5%9F%B9%E7%B3%BB%E7%BB%9Fclassropm-course-statistics%E5%AD%98%E5%9C%A8%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96%E6%BC%8F%E6%B4%9E.md
