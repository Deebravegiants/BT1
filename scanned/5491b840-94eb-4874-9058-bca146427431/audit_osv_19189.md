# [M] CVE-2020-8617

## Summary
Severity: Medium
Advisory: CVE-2020-8617
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-8617
Type: osv

## Details
Using a specially-crafted message, an attacker may potentially cause a BIND server to reach an inconsistent state if the attacker knows (or successfully guesses) the name of a TSIG key used by the server. Since BIND, by default, configures a local session key even on servers whose configuration does not otherwise make use of it, almost all current BIND servers are vulnerable. In releases of BIND dating from March 2018 and after, an assertion check in tsig.c detects this inconsistent state and deliberately exits. Prior to the introduction of the check the server would continue operating in an inconsistent state, with potentially harmful results.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JKJXVBOKZ36ER3EUCR7VRB7WGHIIMPNJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WOGCJS2XQ3SQNF4W6GLZ73LWZJ6ZZWZI/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- http://packetstormsecurity.com/files/157836/BIND-TSIG-Denial-Of-Service.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00031.html
- https://security.netapp.com/advisory/ntap-20200522-0002/
- https://usn.ubuntu.com/4365-1/
- https://usn.ubuntu.com/4365-2/
- https://www.debian.org/security/2020/dsa-4689
- http://www.openwall.com/lists/oss-security/2020/05/19/4
- https://kb.isc.org/docs/cve-2020-8617
