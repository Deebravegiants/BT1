# [H] CVE-2017-6891

## Summary
Severity: High
Advisory: CVE-2017-6891
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-22
Source: https://osv.dev/vulnerability/CVE-2017-6891
Type: osv

## Details
Two errors in the "asn1_find_node()" function (lib/parser_aux.c) within GnuTLS libtasn1 version 4.10 can be exploited to cause a stacked-based buffer overflow by tricking a user into processing a specially crafted assignments file via the e.g. asn1Coding utility.

## References
- http://git.savannah.gnu.org/gitweb/?p=libtasn1.git%3Ba=commit%3Bh=5520704d075802df25ce4ffccc010ba1641bd484
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00018.html
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://www.debian.org/security/2017/dsa-3861
- http://www.securityfocus.com/bid/98641
- http://www.securitytracker.com/id/1038619
- https://security.gentoo.org/glsa/201710-11
- https://secuniaresearch.flexerasoftware.com/advisories/76125/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-11/
