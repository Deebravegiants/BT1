# [H] CVE-2020-4031

## Summary
Severity: High
Advisory: CVE-2020-4031
Aliases: GHSA-gwcq-hpq2-m74g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-4031
Type: osv

## Details
In FreeRDP before version 2.1.2, there is a use-after-free in gdi_SelectObject. All FreeRDP clients using compatibility mode with /relax-order-checks are affected. This is fixed in version 2.1.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6Y35HBHG2INICLSGCIKNAR7GCXEHQACQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XOZLH35OJWIQLM7FYDXAP2EAUBDXE76V/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- http://www.freerdp.com/2020/06/22/2_1_2-released
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-gwcq-hpq2-m74g
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4481-1/
- https://github.com/FreeRDP/FreeRDP/commit/6d86e20e1e7caaab4f0c7f89e36d32914dbccc52
