# [H] CVE-2021-22101

## Summary
Severity: High
Advisory: CVE-2021-22101
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-27
Source: https://osv.dev/vulnerability/CVE-2021-22101
Type: osv

## Details
Cloud Controller versions prior to 1.118.0 are vulnerable to unauthenticated denial of Service(DoS) vulnerability allowing unauthenticated attackers to cause denial of service by using REST HTTP requests with label_selectors on multiple V3 endpoints by generating an enormous SQL query.

## References
- https://www.cloudfoundry.org/blog/cve-2021-22101-cloud-controller-is-vulnerable-to-unauthenticated-denial-of-service/
