# [M] CVE-2020-4032

## Summary
Severity: Medium
Advisory: CVE-2020-4032
Aliases: GHSA-3898-mc89-x2vc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-4032
Type: osv

## Details
In FreeRDP before version 2.1.2, there is an integer casting vulnerability in update_recv_secondary_order. All clients with +glyph-cache /relax-order-checks are affected. This is fixed in version 2.1.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6Y35HBHG2INICLSGCIKNAR7GCXEHQACQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XOZLH35OJWIQLM7FYDXAP2EAUBDXE76V/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- http://www.freerdp.com/2020/06/22/2_1_2-released
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-3898-mc89-x2vc
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4481-1/
- https://github.com/FreeRDP/FreeRDP/commit/e7bffa64ef5ed70bac94f823e2b95262642f5296
