# [H] CVE-2018-15754

## Summary
Severity: High
Advisory: CVE-2018-15754
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-13
Source: https://osv.dev/vulnerability/CVE-2018-15754
Type: osv

## Details
Cloud Foundry UAA, versions 60 prior to 66.0, contain an authorization logic error. In environments with multiple identity providers that contain accounts across identity providers with the same username, a remote authenticated user with access to one of these accounts may be able to obtain a token for an account of the same username in the other identity provider.

## References
- http://www.securityfocus.com/bid/106240
- https://www.cloudfoundry.org/blog/cve-2018-15754
- https://www.cloudfoundry.org/blog/cve-2018-15754/
