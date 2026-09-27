# [M] Set Logging Level Without Authentication

## Summary
Severity: Medium
Advisory: CVE-2023-4640
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-08-30
Source: https://osv.dev/vulnerability/CVE-2023-4640
Type: osv

## Details
The controller responsible for setting the logging level does not include any authorization
checks to ensure the user is authenticated. This can be seen by noting that it extends
Controller rather than AuthenticatedController and includes no further checks. This issue affects YugabyteDB Anywhere: from 2.0.0 through 2.17.3

## References
- https://www.yugabyte.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4640.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4640
- https://github.com/yugabyte/yugabyte-db
