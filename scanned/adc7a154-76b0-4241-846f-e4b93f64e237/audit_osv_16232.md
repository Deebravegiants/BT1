# [H] CVE-2019-3798

## Summary
Severity: High
Advisory: CVE-2019-3798
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-17
Source: https://osv.dev/vulnerability/CVE-2019-3798
Type: osv

## Details
Cloud Foundry Cloud Controller API Release, versions prior to 1.79.0, contains improper authentication when validating user permissions. A remote authenticated malicious user with the ability to create UAA clients and knowledge of the email of a victim in the foundation may escalate their privileges to that of the victim by creating a client with a name equal to the guid of their victim.

## References
- http://www.securityfocus.com/bid/108095
- https://www.cloudfoundry.org/blog/cve-2019-3798
