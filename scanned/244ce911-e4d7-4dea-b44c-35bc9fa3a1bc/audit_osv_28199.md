# [M] snapd will follow archived symlinks when unpacking a filesystem

## Summary
Severity: Medium
Advisory: CVE-2024-29069
Aliases: GHSA-69p6-gp5x-j269, GO-2024-3009
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-07-25
Source: https://osv.dev/vulnerability/CVE-2024-29069
Type: osv

## Details
In snapd versions prior to 2.62, snapd failed to properly check the
destination of symbolic links when extracting a snap. The snap format 
is a squashfs file-system image and so can contain symbolic links and
other file types. Various file entries within the snap squashfs image
(such as icons and desktop files etc) are directly read by snapd when
it is extracted. An attacker who could convince a user to install a
malicious snap which contained symbolic links at these paths could then 
cause snapd to write out the contents of the symbolic link destination
into a world-readable directory. This in-turn could allow an unprivileged
user to gain access to privileged information.

## References
- https://github.com/snapcore/snapd/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29069.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29069
- https://github.com/snapcore/snapd/pull/13682
