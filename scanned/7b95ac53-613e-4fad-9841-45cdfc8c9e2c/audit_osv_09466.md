# [H] CVE-2016-9954

## Summary
Severity: High
Advisory: CVE-2016-9954
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-21
Source: https://osv.dev/vulnerability/CVE-2016-9954
Type: osv

## Details
The backtrack compilation code in the Irregex package (aka IrRegular Expressions) before 0.9.6 for Scheme allows remote attackers to cause a denial of service (memory consumption) via a crafted regular expression with a repeating pattern.

## References
- http://www.openwall.com/lists/oss-security/2016/12/15/8
- http://www.securityfocus.com/bid/94942
- https://bugzilla.redhat.com/show_bug.cgi?id=1413990
- https://github.com/ashinn/irregex/commit/a16ffc86eca15fca9e40607d41de3cea9cf868f1
