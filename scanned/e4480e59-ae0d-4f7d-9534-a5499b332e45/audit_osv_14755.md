# [M] CVE-2019-11282

## Summary
Severity: Medium
Advisory: CVE-2019-11282
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-11282
Type: osv

## Details
Cloud Foundry UAA, versions prior to v74.3.0, contains an endpoint that is vulnerable to SCIM injection attack. A remote authenticated malicious user with scim.invite scope can craft a request with malicious content which can leak information about users of the UAA.

## References
- https://www.cloudfoundry.org/blog/cve-2019-11282
