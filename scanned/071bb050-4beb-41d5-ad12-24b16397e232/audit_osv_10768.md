# [H] CVE-2017-2590

## Summary
Severity: High
Advisory: CVE-2017-2590
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2590
Type: osv

## Details
A vulnerability was found in ipa before 4.4. IdM's ca-del, ca-disable, and ca-enable commands did not properly check the user's permissions while modifying CAs in Dogtag. An authenticated, unauthorized attacker could use this flaw to delete, disable, or enable CAs causing various denial of service problems with certificate issuance, OCSP signing, and deletion of secret keys.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0388.html
- http://www.securityfocus.com/bid/96557
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2590
