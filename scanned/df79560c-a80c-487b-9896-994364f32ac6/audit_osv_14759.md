# [M] CVE-2019-11293

## Summary
Severity: Medium
Advisory: CVE-2019-11293
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-06
Source: https://osv.dev/vulnerability/CVE-2019-11293
Type: osv

## Details
Cloud Foundry UAA Release, versions prior to v74.10.0, when set to logging level DEBUG, logs client_secret credentials when sent as a query parameter. A remote authenticated malicious user could gain access to user credentials via the uaa.log file if authentication is provided via query parameters.

## References
- https://www.cloudfoundry.org/blog/cve-2019-11293
