# [M] CVE-2022-42969

## Summary
Severity: Medium
Advisory: CVE-2022-42969
CVSS: 5.3 (CVSS:3.1/AC:L/AV:N/A:L/C:N/I:N/PR:N/S:U/UI:N)
Published: 2022-10-16
Source: https://osv.dev/vulnerability/CVE-2022-42969
Type: osv

## Details
The py library through 1.11.0 for Python allows remote attackers to conduct a ReDoS (Regular expression Denial of Service) attack via a Subversion repository with crafted info data, because the InfoSvnCommand argument is mishandled. Note: This has been disputed by multiple third parties as not being reproduceable and they argue this is not a valid vulnerability.

## References
- https://github.com/pytest-dev/py/blob/cb87a83960523a2367d0f19226a73aed4ce4291d/py/_path/svnurl.py#L316
- https://news.ycombinator.com/item?id=34163710
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42969.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42969
- https://github.com/pytest-dev/py/issues/287
- https://pypi.org/project/py
