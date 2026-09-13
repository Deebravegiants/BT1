# [C] CVE-2020-8597

## Summary
Severity: Critical
Advisory: CVE-2020-8597
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-03
Source: https://osv.dev/vulnerability/CVE-2020-8597
Type: osv

## Details
eap.c in pppd in ppp 2.4.2 through 2.4.8 has an rhostname buffer overflow in the eap_request and eap_response functions.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UNJNHWOO4XF73M2W56ILZUY4JQG3JXIR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YOFDAIOWSWPG732ASYUZNINMXDHY4APE/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00006.html
- http://packetstormsecurity.com/files/156662/pppd-2.4.8-Buffer-Overflow.html
- http://packetstormsecurity.com/files/156802/pppd-2.4.8-Buffer-Overflow.html
- http://seclists.org/fulldisclosure/2020/Mar/6
- https://access.redhat.com/errata/RHSA-2020:0630
- https://access.redhat.com/errata/RHSA-2020:0631
- https://access.redhat.com/errata/RHSA-2020:0633
- https://access.redhat.com/errata/RHSA-2020:0634
- https://cert-portal.siemens.com/productcert/pdf/ssa-809841.pdf
- https://kb.netgear.com/000061806/Security-Advisory-for-Unauthenticated-Remote-Buffer-Overflow-Attack-in-PPPD-on-WAC510-PSV-2020-0136
- https://lists.debian.org/debian-lts-announce/2020/02/msg00005.html
- https://security.gentoo.org/glsa/202003-19
- https://security.netapp.com/advisory/ntap-20200313-0004/
- https://us-cert.cisa.gov/ics/advisories/icsa-20-224-04
- https://usn.ubuntu.com/4288-1/
- https://usn.ubuntu.com/4288-2/
- https://www.debian.org/security/2020/dsa-4632
- https://www.kb.cert.org/vuls/id/782301
