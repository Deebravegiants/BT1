# [H] CVE-2017-9334

## Summary
Severity: High
Advisory: CVE-2017-9334
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-01
Source: https://osv.dev/vulnerability/CVE-2017-9334
Type: osv

## Details
An incorrect "pair?" check in the Scheme "length" procedure results in an unsafe pointer dereference in all CHICKEN Scheme versions prior to 4.13, which allows an attacker to cause a denial of service by passing an improper list to an application that calls "length" on it.

## References
- http://lists.nongnu.org/archive/html/chicken-announce/2017-05/msg00000.html
- http://lists.nongnu.org/archive/html/chicken-hackers/2017-05/msg00099.html
