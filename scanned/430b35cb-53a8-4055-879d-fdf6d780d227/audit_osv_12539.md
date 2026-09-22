# [M] CVE-2018-1269

## Summary
Severity: Medium
Advisory: CVE-2018-1269
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-06
Source: https://osv.dev/vulnerability/CVE-2018-1269
Type: osv

## Details
Cloud Foundry Loggregator, versions 89.x prior to 89.5 or 96.x prior to 96.1 or 99.x prior to 99.1 or 101.x prior to 101.9 or 102.x prior to 102.2, does not handle errors thrown while constructing certain http requests. A remote authenticated user may construct malicious requests to cause the traffic controller to leave dangling TCP connections, which could cause denial of service.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1269
