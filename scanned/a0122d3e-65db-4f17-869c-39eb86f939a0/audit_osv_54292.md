# [H] CVE-2023-46838

## Summary
Severity: High
Advisory: CVE-2023-46838
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-29
Source: https://osv.dev/vulnerability/CVE-2023-46838
Type: osv

## Details
Transmit requests in Xen's virtual network protocol can consist of
multiple parts.  While not really useful, except for the initial part
any of them may be of zero length, i.e. carry no data at all.  Besides a
certain initial portion of the to be transferred data, these parts are
directly translated into what Linux calls SKB fragments.  Such converted
request parts can, when for a particular SKB they are all of length
zero, lead to a de-reference of NULL in core networking code.

## References
- http://xenbits.xen.org/xsa/advisory-448.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://xenbits.xenproject.org/xsa/advisory-448.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZFYW6R64GPLUOXSQBJI3JBUX3HGLAYPP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RGEKT4DKSDXDS34EL7M4UVJMMPH7Z3ZZ/
