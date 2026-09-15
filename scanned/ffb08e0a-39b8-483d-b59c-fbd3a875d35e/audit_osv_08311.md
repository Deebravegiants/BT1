# [H] CVE-2016-2183

## Summary
Severity: High
Advisory: CVE-2016-2183
Aliases: PSF-2016-4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-01
Source: https://osv.dev/vulnerability/CVE-2016-2183
Type: osv

## Details
The DES and Triple DES ciphers, as used in the TLS, SSH, and IPSec protocols and other protocols and products, have a birthday bound of approximately four billion blocks, which makes it easier for remote attackers to obtain cleartext data via a birthday attack against a long-duration encrypted session, as demonstrated by an HTTPS session using Triple DES in CBC mode, aka a "Sweet32" attack.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://www.vicarius.io/vsociety/posts/cve-2016-2183-detection-sweet32-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2016-2183-mitigate-sweet32-vulnerability
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00068.html
- http://lists.opensuse.org/opensuse-security-announce/2017-02/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2017-02/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2017-02/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2017-02/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2017-05/msg00076.html
