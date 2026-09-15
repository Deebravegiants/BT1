# [M] CVE-2021-3997

## Summary
Severity: Medium
Advisory: CVE-2021-3997
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3997
Type: osv

## Details
A flaw was found in systemd. An uncontrolled recursion in systemd-tmpfiles may lead to a denial of service at boot time when too many nested directories are created in /tmp.

## References
- https://security.gentoo.org/glsa/202305-15
- https://access.redhat.com/security/cve/CVE-2021-3997
- https://bugzilla.redhat.com/show_bug.cgi?id=2024639
- https://github.com/systemd/systemd/commit/5b1cf7a9be37e20133c0208005274ce4a5b5c6a1
- https://www.openwall.com/lists/oss-security/2022/01/10/2
