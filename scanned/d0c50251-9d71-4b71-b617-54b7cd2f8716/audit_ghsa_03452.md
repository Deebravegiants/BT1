# [H] Improper Certificate Validation in blackduck

## Summary
Severity: High
Advisory: GHSA-f248-v4qh-x2r6
CVE: CVE-2020-27589
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-f248-v4qh-x2r6
Type: github-advisory

## Affected
- PyPI: `blackduck` — affected >=0.0.25 <0.0.53

## Details
Synopsys hub-rest-api-python (aka blackduck on PyPI) version 0.0.25 - 0.0.52 does not validate SSL certificates in certain cases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27589
- https://github.com/blackducksoftware/hub-rest-api-python/pull/113
- https://github.com/blackducksoftware/hub-rest-api-python/commit/0a25777117515b8b4ff287a98f57837a8c6bdbdb
- https://community.synopsys.com/s/question/0D52H00005JCZAXSA5/announcement-black-duck-defect-identified
- https://github.com/advisories/GHSA-f248-v4qh-x2r6
- https://github.com/blackducksoftware/hub-rest-api-python
- https://github.com/pypa/advisory-database/tree/main/vulns/blackduck/PYSEC-2020-26.yaml
- https://pypi.org/project/blackduck
- https://www.optiv.com/explore-optiv-insights/source-zero/certificate-validation-disabled-black-duck-api-wrapper
