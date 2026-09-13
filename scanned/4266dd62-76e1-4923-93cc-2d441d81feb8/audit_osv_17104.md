# [C] CVE-2020-12460

## Summary
Severity: Critical
Advisory: CVE-2020-12460
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-27
Source: https://osv.dev/vulnerability/CVE-2020-12460
Type: osv

## Details
OpenDMARC through 1.3.2 and 1.4.x through 1.4.0-Beta1 has improper null termination in the function opendmarc_xml_parse that can result in a one-byte heap overflow in opendmarc_xml when parsing a specially crafted DMARC aggregate report. This can cause remote memory corruption when a '\0' byte overwrites the heap metadata of the next chunk and its PREV_INUSE flag.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2D4JGHMALEJEWWG56DKR5OZB22TK7W5B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JHDKMCZGE3W4XBP76NLI2Q7IOZHXLD4A/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KBOGOQOK3TIWWJV66MW5YWNRJAFFYGR5/
- https://lists.debian.org/debian-lts-announce/2021/04/msg00026.html
- https://security.gentoo.org/glsa/202011-02
- https://sourceforge.net/projects/opendmarc/
- https://github.com/trusteddomainproject/OpenDMARC/issues/64
