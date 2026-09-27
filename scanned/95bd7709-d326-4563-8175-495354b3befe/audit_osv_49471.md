# [M] CVE-2019-13075

## Summary
Severity: Medium
Advisory: CVE-2019-13075
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/CVE-2019-13075
Type: osv

## Details
Tor Browser through 8.5.3 has an information exposure vulnerability. It allows remote attackers to detect the browser's language via vectors involving an IFRAME element, because text in that language is included in the title attribute of a LINK element for a non-HTML page. This is related to a behavior of Firefox before 68.

## References
- https://trac.torproject.org/projects/tor/ticket/30657
- https://hackerone.com/reports/588239
