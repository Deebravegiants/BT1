# [H] CVE-2021-43833

## Summary
Severity: High
Advisory: CVE-2021-43833
Aliases: GHSA-v659-q2fh-v99w
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-16
Source: https://osv.dev/vulnerability/CVE-2021-43833
Type: osv

## Details
eLabFTW is an electronic lab notebook manager for research teams. In versions prior to 4.2.0 there is a vulnerability which allows any authenticated user to gain access to arbitrary accounts by setting a specially crafted email address. This vulnerability impacts all instances that have not set an explicit email domain name allowlist. Note that whereas neither administrators nor targeted users are notified of a change, an attacker will need to control an account. The default settings require administrators to validate newly created accounts. The problem has been patched. Users should upgrade to at least version 4.2.0. For users unable to upgrade enabling an email domain allow list (from Sysconfig panel, Security tab) will completely resolve the issue.

## References
- https://github.com/elabftw/elabftw/releases/tag/4.2.0
- https://github.com/elabftw/elabftw/security/advisories/GHSA-v659-q2fh-v99w
