# [M] CVE-2017-11104

## Summary
Severity: Medium
Advisory: CVE-2017-11104
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-07-08
Source: https://osv.dev/vulnerability/CVE-2017-11104
Type: osv

## Details
Knot DNS before 2.4.5 and 2.5.x before 2.5.2 contains a flaw within the TSIG protocol implementation that would allow an attacker with a valid key name and algorithm to bypass TSIG authentication if no additional ACL restrictions are set, because of an improper TSIG validity period check.

## References
- http://www.securityfocus.com/bid/99598
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00076.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00089.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00049.html
- http://www.debian.org/security/2017/dsa-3910
- https://bugs.debian.org/865678
- http://www.synacktiv.ninja/ressources/Knot_DNS_TSIG_Signature_Forgery.pdf
- https://lists.nic.cz/pipermail/knot-dns-users/2017-June/001144.html
