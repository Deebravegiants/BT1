# [M] CVE-2024-6388

## Summary
Severity: Medium
Advisory: CVE-2024-6388
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-6388
Type: osv

## Details
Marco Trevisan discovered that the Ubuntu Advantage Desktop Daemon, before version 1.12, leaks the Pro token to unprivileged users by passing the token as an argument in plaintext.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6388.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6388
- https://bugs.launchpad.net/ubuntu/+source/ubuntu-advantage-tools/+bug/2068944
- https://github.com/canonical/ubuntu-advantage-desktop-daemon/pull/24
- https://www.cve.org/CVERecord?id=CVE-2024-6388
- https://github.com/canonical/ubuntu-advantage-desktop-daemon
