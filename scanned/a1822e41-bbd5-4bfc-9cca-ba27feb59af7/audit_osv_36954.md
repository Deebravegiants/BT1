# [M] util-linux: TOCTOU Race Condition in util-linux mount(8) - Loop Device Setup

## Summary
Severity: Medium
Advisory: CVE-2026-27456
Aliases: GHSA-qq4x-vfq4-9h9g
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-27456
Type: osv

## Details
util-linux is a random collection of Linux utilities. Prior to version 2.41.4, a TOCTOU (Time-of-Check-Time-of-Use) vulnerability has been identified in the SUID binary /usr/bin/mount from util-linux. The mount binary, when setting up loop devices, validates the source file path with user privileges via fork() + setuid() + realpath(), but subsequently re-canonicalizes and opens it with root privileges (euid=0) without verifying that the path has not been replaced between both operations. Neither O_NOFOLLOW, nor inode comparison, nor post-open fstat() are employed. This allows a local unprivileged user to replace the source file with a symlink pointing to any root-owned file or device during the race window, causing the SUID binary to open and mount it as root. Exploitation requires an /etc/fstab entry with user,loop options whose path points to a directory where the attacker has write permission, and that /usr/bin/mount has the SUID bit set (the default configuration on virtually all Linux distributions). The impact is unauthorized read access to root-protected files and block devices, including backup images, disk volumes, and any file containing a valid filesystem. This issue has been patched in version 2.41.4.

## References
- https://github.com/util-linux/util-linux/releases/tag/v2.41.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27456.json
- https://github.com/util-linux/util-linux/security/advisories/GHSA-qq4x-vfq4-9h9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-27456
- https://github.com/util-linux/util-linux/commit/5e390467b26a3cf3fecc04e1a0d482dff3162fc4
