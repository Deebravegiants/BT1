# [M] Apache XML Security For Java vulnerable to authentication bypass by HMAC truncation

## Summary
Severity: Medium
Advisory: GHSA-8hfm-837h-hjg5
CVE: CVE-2009-0217
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-8hfm-837h-hjg5
Type: github-advisory

## Affected
- Maven: `org.apache.santuario:xmlsec` — affected >=1.4.0 <1.4.3

## Details
The design of the W3C XML Signature Syntax and Processing (XMLDsig) recommendation, as implemented in multiple products.

The Apache XML Security (Java) is affected by the vulnerability published in US-Cert VU #466161. See: http://www.kb.cert.org/vuls/id/466161 for more information. This bug can allow an attacker to bypass authentication by inserting/modifying a small HMAC truncation length parameter in the XML Signature HMAC based SignatureMethod algorithms.

An inexhaustive list of additional affected products includes:  
1. the Oracle Security Developer Tools component in Oracle Application Server 10.1.2.3, 10.1.3.4, and 10.1.4.3IM; 
2. the WebLogic Server component in BEA Product Suite 10.3, 10.0 MP1, 9.2 MP3, 9.1, 9.0, and 8.1 SP6; 
3. Mono before 2.4.2.2; 
4. XML Security Library before 1.2.12; 
5. IBM WebSphere Application Server Versions 6.0 through 6.0.2.33, 6.1 through 6.1.0.23, and 7.0 through 7.0.0.1; 
6. Sun JDK and JRE Update 14 and earlier; 
7. Microsoft .NET Framework 3.0 through 3.0 SP2, 3.5, and 4.0; and other products uses a parameter that defines an HMAC truncation length (HMACOutputLength) but does not require a minimum for this length, which allows attackers to spoof HMAC-based signatures and bypass authentication by specifying a truncation length with a small number of bits.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0217
- https://www.w3.org/QA/2009/07/hmac_truncation_in_xml_signatu.html
- https://www.w3.org/2008/06/xmldsigcore-errata.html#e03
- https://www.us-cert.gov/cas/techalerts/TA09-294A.html
- https://www.ubuntu.com/usn/USN-903-1
- https://www.redhat.com/support/errata/RHSA-2009-1694.html
- https://www.redhat.com/archives/fedora-package-announce/2009-August/msg00505.html
- https://www.redhat.com/archives/fedora-package-announce/2009-August/msg00494.html
- https://www.redhat.com/archives/fedora-package-announce/2009-August/msg00325.html
- https://www.redhat.com/archives/fedora-package-announce/2009-August/msg00310.html
- https://www.mandriva.com/security/advisories?name=MDVSA-2009:209
- https://www.kb.cert.org/vuls/id/WDON-7TY529
- https://www.kb.cert.org/vuls/id/MAPG-7TSKXQ
- https://www.kb.cert.org/vuls/id/466161
- https://www.gentoo.org/security/en/glsa/glsa-201408-19.xml
- https://www.debian.org/security/2010/dsa-1995
- https://svn.apache.org/viewvc?revision=794013&view=revision
- https://rhn.redhat.com/errata/RHSA-2009-1428.html
- https://marc.info/?l=bugtraq&m=125787273209737&w=2
- https://lists.opensuse.org/opensuse-security-announce/2010-03/msg00005.html
