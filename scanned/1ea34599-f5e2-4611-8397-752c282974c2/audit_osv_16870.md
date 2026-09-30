# [H] CVE-2020-10174

## Summary
Severity: High
Advisory: CVE-2020-10174
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/CVE-2020-10174
Type: osv

## Details
init_tmp in TeeJee.FileSystem.vala in Timeshift before 20.03 unsafely reuses a preexisting temporary directory in the predictable location /tmp/timeshift. It follows symlinks in this location or uses directories owned by unprivileged users. Because Timeshift also executes scripts under this location, an attacker can attempt to win a race condition to replace scripts created by Timeshift with attacker-controlled scripts. Upon success, an attacker-controlled script is executed with full root privileges. This logic is practically always triggered when Timeshift runs regardless of the command-line arguments used.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AAOFXT64CEUMJE3723JDJWTEQWQUCYMD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SXDEPC52G46U6I7GLQNFLZXVSM7V2HYY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TXXYQFSZ5P6ZMNFIDBAQKBFZIR2T7ZLL/
- http://www.openwall.com/lists/oss-security/2020/03/06/3
- https://github.com/teejee2008/timeshift/releases/tag/v20.03
- https://usn.ubuntu.com/4312-1/
- https://bugzilla.suse.com/show_bug.cgi?id=1165802
- https://github.com/teejee2008/timeshift/commit/335b3d5398079278b8f7094c77bfd148b315b462
