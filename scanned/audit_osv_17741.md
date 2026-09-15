# [H] CVE-2020-1930

## Summary
Severity: High
Advisory: CVE-2020-1930
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-30
Source: https://osv.dev/vulnerability/CVE-2020-1930
Type: osv

## Details
A command execution issue was found in Apache SpamAssassin prior to 3.4.3. Carefully crafted nefarious rule configuration (.cf) files can be configured to run system commands similar to CVE-2018-11805. With this bug unpatched, exploits can be injected in a number of scenarios including the same privileges as spamd is run which may be elevated though doing so remotely is difficult. In addition to upgrading to SA 3.4.4, we again recommend that users should only use update channels or 3rd party .cf files from trusted places. If you cannot upgrade, do not use 3rd party rulesets, do not use sa-compile and do not run spamd as an account with elevated privileges.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00003.html
- https://lists.apache.org/thread.html/r6729f3d3be754a06c39bb4f11c925a3631e8ea2b4c865546d755cb0a%40%3Cannounce.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/02/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B7SY2LUSH2X3IUXN4EQQ5A6QVUFYIV3D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VOVVKFP2G2AF5GHAB4WMHOEX76A3H6CE/
- https://seclists.org/bugtraq/2020/Feb/1
- https://usn.ubuntu.com/4265-1/
- https://usn.ubuntu.com/4265-2/
- https://www.debian.org/security/2020/dsa-4615
- https://bz.apache.org/SpamAssassin/show_bug.cgi?id=7648
