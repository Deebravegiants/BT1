# [H] CVE-2017-18926

## Summary
Severity: High
Advisory: CVE-2017-18926
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/CVE-2017-18926
Type: osv

## Details
raptor_xml_writer_start_element_common in raptor_xml_writer.c in Raptor RDF Syntax Library 2.0.15 miscalculates the maximum nspace declarations for the XML writer, leading to heap-based buffer overflows (sometimes seen in raptor_qname_format_as_xml).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RD67AVORGQXORPWNYYUHCH6YPPT6CI4O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WDZRNM45VPTQF2BKRWG4YRCHJGQ2L7NS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RVHFYQDMVEBICIL4DBAGRRLPUR4QYWMV/
- https://lists.debian.org/debian-lts-announce/2020/11/msg00012.html
- http://www.openwall.com/lists/oss-security/2020/11/13/2
- http://www.openwall.com/lists/oss-security/2020/11/14/2
- http://www.openwall.com/lists/oss-security/2020/11/16/2
- http://www.openwall.com/lists/oss-security/2020/11/16/3
- https://www.debian.org/security/2020/dsa-4785
- http://www.openwall.com/lists/oss-security/2020/11/13/1
- https://github.com/LibreOffice/core/blob/master/external/redland/raptor/0001-Calcualte-max-nspace-declarations-correctly-for-XML-.patch.1
- https://www.openwall.com/lists/oss-security/2017/06/07/1
