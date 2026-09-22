# [H] CVE-2019-9810

## Summary
Severity: High
Advisory: CVE-2019-9810
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2019-9810
Type: osv

## Details
Incorrect alias information in IonMonkey JIT compiler for Array.prototype.slice method may lead to missing bounds check and a buffer overflow. This vulnerability affects Firefox < 66.0.1, Firefox ESR < 60.6.1, and Thunderbird < 60.6.1.

## References
- https://access.redhat.com/errata/RHSA-2019:0966
- https://access.redhat.com/errata/RHSA-2019:1144
- https://www.mozilla.org/security/advisories/mfsa2019-09/
- https://www.mozilla.org/security/advisories/mfsa2019-10/
- https://www.mozilla.org/security/advisories/mfsa2019-12/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1537924
- http://packetstormsecurity.com/files/155592/Mozilla-Firefox-Windows-64-Bit-Chain-Exploit.html
