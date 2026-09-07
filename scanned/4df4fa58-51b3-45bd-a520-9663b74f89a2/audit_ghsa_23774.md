# [H] Scrapy denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-h7wm-ph43-c39p
CVE: CVE-2017-14158
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h7wm-ph43-c39p
Type: github-advisory

## Affected
- PyPI: `scrapy` — affected >=0.7

## Details
Scrapy 1.4 allows remote attackers to cause a denial of service (memory consumption) via large files because arbitrarily many files are read into memory, which is especially problematic if the files are then individually written in a separate thread to a slow storage resource, as demonstrated by interaction between dataReceived (in core/downloader/handlers/http11.py) and S3FilesStore.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14158
- https://github.com/scrapy/scrapy/issues/482
- https://github.com/pypa/advisory-database/blob/8b7a4d62a95e8f605e5dfb4e0b4f299e6403dc12/vulns/scrapy/PYSEC-2017-83.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/scrapy/PYSEC-2017-83.yaml
- https://github.com/scrapy/scrapy
- http://blog.csdn.net/wangtua/article/details/75228728
