# [H] CVE-2018-1266

## Summary
Severity: High
Advisory: CVE-2018-1266
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2018-1266
Type: osv

## Details
Cloud Foundry Cloud Controller, versions prior to 1.52.0, contains information disclosure and path traversal vulnerabilities. An authenticated malicious user can predict the location of application blobs and leverage path traversal to create a malicious application that has the ability to overwrite arbitrary files on the Cloud Controller instance.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1266/
