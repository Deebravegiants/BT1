# [H] CVE-2017-1000363

## Summary
Severity: High
Advisory: CVE-2017-1000363
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-1000363
Type: osv

## Details
Linux drivers/char/lp.c Out-of-Bounds Write. Due to a missing bounds check, and the fact that parport_ptr integer is static, a 'secure boot' kernel command line adversary (can happen due to bootloader vulns, e.g. Google Nexus 6's CVE-2016-10277, where due to a vulnerability the adversary has partial control over the command line) can overflow the parport_nr array in the following code, by appending many (>LP_NO) 'lp=none' arguments to the command line.

## References
- http://www.debian.org/security/2017/dsa-3945
- http://www.securityfocus.com/bid/98651
- https://alephsecurity.com/vulns/aleph-2017023
