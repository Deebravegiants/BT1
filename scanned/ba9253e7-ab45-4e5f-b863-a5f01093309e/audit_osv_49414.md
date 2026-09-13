# [H] CVE-2019-11745

## Summary
Severity: High
Advisory: CVE-2019-11745
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-11745
Type: osv

## Details
When encrypting with a block cipher, if a call to NSC_EncryptUpdate was made with data smaller than the block size, a small out of bounds write could occur. This could have caused heap corruption and a potentially exploitable crash. This vulnerability affects Thunderbird < 68.3, Firefox ESR < 68.3, and Firefox < 71.

## References
- https://access.redhat.com/errata/RHSA-2020:0243
- https://security.gentoo.org/glsa/202003-10
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2019-38/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00006.html
- https://access.redhat.com/errata/RHSA-2020:0466
- https://security.gentoo.org/glsa/202003-37
- https://usn.ubuntu.com/4241-1/
- https://cert-portal.siemens.com/productcert/pdf/ssa-379803.pdf
- https://lists.debian.org/debian-lts-announce/2020/09/msg00029.html
- https://security.gentoo.org/glsa/202003-02
- https://us-cert.cisa.gov/ics/advisories/icsa-21-040-04
- https://www.mozilla.org/security/advisories/mfsa2019-36/
- https://www.mozilla.org/security/advisories/mfsa2019-37/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00001.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1586176
