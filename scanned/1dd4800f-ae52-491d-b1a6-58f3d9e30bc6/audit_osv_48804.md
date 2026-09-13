# [M] CVE-2018-14526

## Summary
Severity: Medium
Advisory: CVE-2018-14526
CVSS: 6.5 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-08
Source: https://osv.dev/vulnerability/CVE-2018-14526
Type: osv

## Details
An issue was discovered in rsn_supp/wpa.c in wpa_supplicant 2.0 through 2.6. Under certain conditions, the integrity of EAPOL-Key messages is not checked, leading to a decryption oracle. An attacker within range of the Access Point and client can abuse the vulnerability to recover sensitive information.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00013.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-344983.pdf
- https://usn.ubuntu.com/3745-1/
- https://access.redhat.com/errata/RHSA-2018:3107
- https://lists.debian.org/debian-lts-announce/2018/08/msg00009.html
- https://papers.mathyvanhoef.com/woot2018.pdf
- https://www.us-cert.gov/ics/advisories/icsa-19-344-01
- http://www.securitytracker.com/id/1041438
- https://w1.fi/security/2018-1/unauthenticated-eapol-key-decryption.txt
- https://security.FreeBSD.org/advisories/FreeBSD-SA-18:11.hostapd.asc
