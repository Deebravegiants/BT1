# [H] CVE-2022-1271

## Summary
Severity: High
Advisory: CVE-2022-1271
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-1271
Type: osv

## Details
An arbitrary file write vulnerability was found in GNU gzip's zgrep utility. When zgrep is applied on the attacker's chosen file name (for example, a crafted file name), this can overwrite an attacker's content to an arbitrary attacker-selected file. This flaw occurs due to insufficient validation when processing filenames with two or more newlines where selected content and the target file names are embedded in crafted multi-line file names. This flaw allows a remote, low privileged attacker to force zgrep to write arbitrary files on the system.

## References
- https://access.redhat.com/security/cve/CVE-2022-1271
- https://git.tukaani.org/?p=xz.git%3Ba=commit%3Bh=69d1b3fc29677af8ade8dc15dba83f0589cb63d6
- https://lists.gnu.org/r/bug-gzip/2022-04/msg00011.html
- https://security-tracker.debian.org/tracker/CVE-2022-1271
- https://tukaani.org/xz/xzgrep-ZDI-CAN-16587.patch
- https://www.openwall.com/lists/oss-security/2022/04/07/8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1271.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1271
- https://security.gentoo.org/glsa/202209-01
- https://security.netapp.com/advisory/ntap-20220930-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2073310
