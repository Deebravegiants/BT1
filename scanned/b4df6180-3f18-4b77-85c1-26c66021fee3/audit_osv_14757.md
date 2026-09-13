# [H] CVE-2019-11290

## Summary
Severity: High
Advisory: CVE-2019-11290
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-11290
Type: osv

## Details
Cloud Foundry UAA Release, versions prior to v74.8.0, logs all query parameters to tomcat’s access file. If the query parameters are used to provide authentication, ie. credentials, then they will be logged as well.

## References
- https://www.cloudfoundry.org/blog/cve-2019-11290
