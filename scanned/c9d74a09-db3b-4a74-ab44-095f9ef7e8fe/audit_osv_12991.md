# [H] CVE-2018-16807

## Summary
Severity: High
Advisory: CVE-2018-16807
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-11
Source: https://osv.dev/vulnerability/CVE-2018-16807
Type: osv

## Details
In Bro through 2.5.5, there is a memory leak potentially leading to DoS in scripts/base/protocols/krb/main.bro in the Kerberos protocol parser.

## References
- https://github.com/bro/bro/commit/34d0cf886ca16c665f673a299e295b2a2bc14533
