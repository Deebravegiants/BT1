# [H] XXE vulnerability in Launch import

## Summary
Severity: High
Advisory: GHSA-2jx8-v4hv-gx3h
CVE: CVE-2020-12642
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-28
Source: https://github.com/advisories/GHSA-2jx8-v4hv-gx3h
Type: github-advisory

## Affected
- Maven: `com.epam.reportportal:service-api` — affected >=3.1.0 <4.3.12
- Maven: `com.epam.reportportal:service-api` — affected >=5.0.0 <5.1.1

## Details
| Release Date | Affected Projects | Affected Versions | Access Vector| Security Risk |
|--------------|-------------------|-------------------|---------------|---------------|
| Monday, May 4, 2020| [service-api](https://github.com/reportportal/service-api) | Every version, starting from 3.1.0 | Remote | Medium |

### Impact
Starting from version 3.1.0 we introduced a new feature of JUnit XML launch import. Unfortunately XML parser was not configured properly to prevent XML external entity (XXE) attacks. This allows a user to import a specifically-crafted XML file that uses external entities for extraction of secrets from Report Portal service-api module or server-side request forgery.

Report Portal versions 4.3.12+ and 5.1.1+ disables external entity resolution for theirs XML parser.

We advise our users install the latest releases we built specifically to address this issue.

### Patches
Fixed with https://github.com/reportportal/service-api/pull/1201

### Binary Download
https://bintray.com/epam/reportportal/service-api/5.1.1
https://bintray.com/epam/reportportal/service-api/4.3.12

### Docker Container Download
* RP v4: `docker pull reportportal/service-api:4.3.12`
* RP v5: `docker pull reportportal/service-api:5.1.1`

### Acknowledgement
The issue was reported to Report Portal Team by an external security researcher.
Our Team thanks Julien M. for reporting the issue.

### For more information
If you have any questions or comments about this advisory email us: [support@reportportal.io](mailto:support@reportportal.io)

## References
- https://github.com/reportportal/reportportal/security/advisories/GHSA-2jx8-v4hv-gx3h
- https://nvd.nist.gov/vuln/detail/CVE-2020-12642
- https://github.com/reportportal/service-api/pull/1201
- https://github.com/reportportal/service-api/commit/da4a012abdcc69f02f4255d81466f1f473b7f418
- https://github.com/reportportal/reportportal
