# [H] CVE-2015-0226

## Summary
Severity: High
Advisory: CVE-2015-0226
Aliases: GHSA-vjwc-5hfh-2vv5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-30
Source: https://osv.dev/vulnerability/CVE-2015-0226
Type: osv

## Details
Apache WSS4J before 1.6.17 and 2.0.x before 2.0.2 improperly leaks information about decryption failures when decrypting an encrypted key or message data, which makes it easier for remote attackers to recover the plaintext form of a symmetric key via a series of crafted messages. NOTE: this vulnerability exists because of an incomplete fix for CVE-2011-2487.

## References
- http://rhn.redhat.com/errata/RHSA-2015-0846.html
- http://rhn.redhat.com/errata/RHSA-2015-0847.html
- http://rhn.redhat.com/errata/RHSA-2015-0848.html
- http://rhn.redhat.com/errata/RHSA-2015-0849.html
- http://rhn.redhat.com/errata/RHSA-2015-1176.html
- http://rhn.redhat.com/errata/RHSA-2015-1177.html
- http://www.securityfocus.com/bid/72553
- https://access.redhat.com/errata/RHSA-2016:1376
- https://ws.apache.org/wss4j/advisories/CVE-2015-0226.txt.asc
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://ws.apache.org/wss4j/advisories/CVE-2015-0226.txt.asc
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbgn03900en_us
