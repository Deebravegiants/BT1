# [H] CVE-2021-29620

## Summary
Severity: High
Advisory: CVE-2021-29620
Aliases: GHSA-24wf-7vf2-pv59
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-23
Source: https://osv.dev/vulnerability/CVE-2021-29620
Type: osv

## Details
Report portal is an open source reporting and analysis framework. Starting from version 3.1.0 of the service-api XML parsing was introduced. Unfortunately the XML parser was not configured properly to prevent XML external entity (XXE) attacks. This allows a user to import a specifically-crafted XML file which imports external Document Type Definition (DTD) file with external entities for extraction of secrets from Report Portal service-api module or server-side request forgery. This will be resolved in the 5.4.0 release.

## References
- https://mvnrepository.com/artifact/com.epam.reportportal/service-api
- https://github.com/reportportal/reportportal/security/advisories/GHSA-24wf-7vf2-pv59
- https://github.com/reportportal/service-api/pull/1392
