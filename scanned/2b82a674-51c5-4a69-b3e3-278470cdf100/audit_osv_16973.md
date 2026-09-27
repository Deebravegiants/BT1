# [H] CVE-2020-11008

## Summary
Severity: High
Advisory: CVE-2020-11008
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-21
Source: https://osv.dev/vulnerability/CVE-2020-11008
Type: osv

## Details
Affected versions of Git have a vulnerability whereby Git can be tricked into sending private credentials to a host controlled by an attacker. This bug is similar to CVE-2020-5260(GHSA-qm7j-c969-7j4q). The fix for that bug still left the door open for an exploit where _some_ credential is leaked (but the attacker cannot control which one). Git uses external "credential helper" programs to store and retrieve passwords or other credentials from secure storage provided by the operating system. Specially-crafted URLs that are considered illegal as of the recently published Git versions can cause Git to send a "blank" pattern to helpers, missing hostname and protocol fields. Many helpers will interpret this as matching _any_ URL, and will return some unspecified stored password, leaking the password to an attacker's server. The vulnerability can be triggered by feeding a malicious URL to `git clone`. However, the affected URLs look rather suspicious; the likely vector would be through systems which automatically clone URLs not visible to the user, such as Git submodules, or package systems built around Git. The root of the problem is in Git itself, which should not be feeding blank input to helpers. However, the ability to exploit the vulnerability in practice depends on which helpers are in use. Credential helpers which are known to trigger the vulnerability: - Git's "store" helper - Git's "cache" helper - the "osxkeychain" helper that ships in Git's "contrib" directory Credential helpers which are known to be safe even with vulnerable versions of Git: - Git Credential Manager for Windows Any helper not in this list should be assumed to trigger the vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00003.html
- http://seclists.org/fulldisclosure/2020/May/41
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/74Q7WVJ6FKLIN62VS2JD2XCNWK5TNKOW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MOCTR2SEHCPSCOVUQJAGFPGKFMI2VE6V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PN3FUOXKX3AXTULYV53ACABER2W2FSOU/
- https://support.apple.com/kb/HT211183
- https://lists.debian.org/debian-lts-announce/2020/04/msg00015.html
- https://security.gentoo.org/glsa/202004-13
- https://usn.ubuntu.com/4334-1/
- https://github.com/git/git/commit/c44088ecc4b0722636e0a305f9608d3047197282
- https://github.com/git/git/security/advisories/GHSA-hjc9-x69f-jqj7
- https://github.com/git/git/security/advisories/GHSA-qm7j-c969-7j4q
