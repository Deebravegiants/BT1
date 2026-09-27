# [M] CVE-2021-22115

## Summary
Severity: Medium
Advisory: CVE-2021-22115
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-22115
Type: osv

## Details
Cloud Controller API versions prior to 1.106.0 logs service broker credentials if the default value of db logging config field is changed. CAPI database logs service broker password in plain text whenever a job to clean up orphaned items is run by Cloud Controller.

## References
- https://www.cloudfoundry.org/blog/cve-2021-22115-capi-logs-service-broker-credentials/
