# [M] CVE-2020-11099

## Summary
Severity: Medium
Advisory: CVE-2020-11099
Aliases: GHSA-977w-866x-4v5h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-11099
Type: osv

## Details
In FreeRDP before version 2.1.2, there is an out of bounds read in license_read_new_or_upgrade_license_packet. A manipulated license packet can lead to out of bound reads to an internal buffer. This is fixed in version 2.1.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6Y35HBHG2INICLSGCIKNAR7GCXEHQACQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XOZLH35OJWIQLM7FYDXAP2EAUBDXE76V/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- http://www.freerdp.com/2020/06/22/2_1_2-released
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-977w-866x-4v5h
- https://usn.ubuntu.com/4481-1/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://github.com/FreeRDP/FreeRDP/commit/6ade7b4cbfd71c54b3d724e8f2d6ac76a58e879a
