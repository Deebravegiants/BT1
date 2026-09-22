# [M] CVE-2020-5404

## Summary
Severity: Medium
Advisory: CVE-2020-5404
Aliases: GHSA-gpch-h32j-gx6x
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2020-03-03
Source: https://osv.dev/vulnerability/CVE-2020-5404
Type: osv

## Details
The HttpClient from Reactor Netty, versions 0.9.x prior to 0.9.5, and versions 0.8.x prior to 0.8.16, may be used incorrectly, leading to a credentials leak during a redirect to a different domain. In order for this to happen, the HttpClient must have been explicitly configured to follow redirects.

## References
- https://pivotal.io/security/cve-2020-5404
