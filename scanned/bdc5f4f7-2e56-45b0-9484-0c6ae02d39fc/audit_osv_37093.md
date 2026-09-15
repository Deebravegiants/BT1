# [H] CVE-2026-28372

## Summary
Severity: High
Advisory: CVE-2026-28372
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28372
Type: osv

## Details
telnetd in GNU inetutils through 2.7 allows privilege escalation that can be exploited by abusing systemd service credentials support added to the login(1) implementation of util-linux in release 2.40. This is related to client control over the CREDENTIALS_DIRECTORY environment variable, and requires an unprivileged local user to create a login.noauth file.

## References
- http://www.openwall.com/lists/oss-security/2026/02/27/3
- http://www.openwall.com/lists/oss-security/2026/03/06/2
- http://www.openwall.com/lists/oss-security/2026/03/06/3
- http://www.openwall.com/lists/oss-security/2026/03/07/1
- http://www.openwall.com/lists/oss-security/2026/03/07/2
- https://git.hadrons.org/cgit/debian/pkgs/inetutils.git/commit/?id=3953943d8296310485f98963883a798545ab9a6c
- https://lists.gnu.org/archive/html/bug-inetutils/2026-02/msg00000.html
- https://lists.gnu.org/archive/html/bug-inetutils/2026-02/msg00012.html
- https://www.openwall.com/lists/oss-security/2026/02/24/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28372.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28372
