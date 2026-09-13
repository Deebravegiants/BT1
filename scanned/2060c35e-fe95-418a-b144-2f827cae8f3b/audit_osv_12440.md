# [H] CVE-2018-12035

## Summary
Severity: High
Advisory: CVE-2018-12035
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12035
Type: osv

## Details
In YARA 3.7.1 and prior, parsing a specially crafted compiled rule file can cause an out of bounds write vulnerability in yr_execute_code in libyara/exec.c.

## References
- https://github.com/VirusTotal/yara/issues/891
- https://bnbdr.github.io/posts/swisscheese/
- https://github.com/bnbdr/swisscheese
