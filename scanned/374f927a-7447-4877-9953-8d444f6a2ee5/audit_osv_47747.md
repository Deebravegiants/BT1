# [H] CVE-2017-11343

## Summary
Severity: High
Advisory: CVE-2017-11343
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11343
Type: osv

## Details
Due to an incomplete fix for CVE-2012-6125, all versions of CHICKEN Scheme up to and including 4.12.0 are vulnerable to an algorithmic complexity attack. An attacker can provide crafted input which, when inserted into the symbol table, will result in O(n) lookup time.

## References
- http://lists.gnu.org/archive/html/chicken-announce/2017-07/msg00000.html
