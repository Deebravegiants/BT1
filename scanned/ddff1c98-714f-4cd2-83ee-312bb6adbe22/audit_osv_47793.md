# [C] CVE-2017-12194

## Summary
Severity: Critical
Advisory: CVE-2017-12194
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-14
Source: https://osv.dev/vulnerability/CVE-2017-12194
Type: osv

## Details
A flaw was found in the way spice-client processed certain messages sent from the server. An attacker, having control of malicious spice-server, could use this flaw to crash the client or execute arbitrary code with permissions of the user running the client. spice-gtk versions through 0.34 are believed to be vulnerable.

## References
- https://usn.ubuntu.com/3659-1/
- http://www.securityfocus.com/bid/103413
- https://security.gentoo.org/glsa/201811-20
- https://bugzilla.redhat.com/show_bug.cgi?id=1501200
