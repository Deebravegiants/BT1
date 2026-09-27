# [M] Cupsd Listen arbitrary chmod 0140777

## Summary
Severity: Medium
Advisory: CVE-2024-35235
Aliases: GHSA-vvwp-mv6j-hw6f
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/CVE-2024-35235
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.8 and earlier, when starting the cupsd server with a Listen configuration item pointing to a symbolic link, the cupsd process can be caused to perform an arbitrary chmod of the provided argument, providing world-writable access to the target. Given that cupsd is often running as root, this can result in the change of permission of any user or system files to be world writable. Given the aforementioned Ubuntu AppArmor context, on such systems this vulnerability is limited to those files modifiable by the cupsd process. In that specific case it was found to be possible to turn the configuration of the Listen argument into full control over the cupsd.conf and cups-files.conf configuration files. By later setting the User and Group arguments in cups-files.conf, and printing with a printer configured by PPD with a `FoomaticRIPCommandLine` argument, arbitrary user and group (not root) command execution could be achieved, which can further be used on Ubuntu systems to achieve full root command execution. Commit ff1f8a623e090dee8a8aadf12a6a4b25efac143d contains a patch for the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/06/11/1
- http://www.openwall.com/lists/oss-security/2024/06/12/4
- http://www.openwall.com/lists/oss-security/2024/06/12/5
- http://www.openwall.com/lists/oss-security/2024/11/08/3
- https://git.launchpad.net/ubuntu/+source/apparmor/tree/profiles/apparmor.d/abstractions/user-tmp#n21
- https://github.com/OpenPrinting/cups/blob/aba917003c8de55e5bf85010f0ecf1f1ddd1408e/cups/http-addr.c#L229-L240
- https://lists.debian.org/debian-lts-announce/2024/06/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35235.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-vvwp-mv6j-hw6f
- https://nvd.nist.gov/vuln/detail/CVE-2024-35235
- https://github.com/OpenPrinting/cups/commit/ff1f8a623e090dee8a8aadf12a6a4b25efac143d
