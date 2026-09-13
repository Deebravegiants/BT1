# [H] CVE-2020-1763

## Summary
Severity: High
Advisory: CVE-2020-1763
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-12
Source: https://osv.dev/vulnerability/CVE-2020-1763
Type: osv

## Details
An out-of-bounds buffer read flaw was found in the pluto daemon of libreswan from versions 3.27 till 3.31 where, an unauthenticated attacker could use this flaw to crash libreswan by sending specially-crafted IKEv1 Informational Exchange packets. The daemon respawns after the crash.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-379803.pdf
- https://security.gentoo.org/glsa/202007-21
- https://us-cert.cisa.gov/ics/advisories/icsa-21-040-04
- https://www.debian.org/security/2020/dsa-4684
- https://bugzilla.redhat.com/show_bug.cgi?id=1813329
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1763
- https://github.com/libreswan/libreswan/commit/471a3e41a449d7c753bc4edbba4239501bb62ba8
- https://libreswan.org/security/CVE-2020-1763/CVE-2020-1763.txt
