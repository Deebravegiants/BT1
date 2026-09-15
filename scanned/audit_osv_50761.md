# [H] CVE-2020-37182

## Summary
Severity: High
Advisory: CVE-2020-37182
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2020-37182
Type: osv

## Details
Redir 3.3 contains a stack overflow vulnerability in the doproxyconnect() function that allows attackers to crash the application by sending oversized input. Attackers can exploit the sprintf() buffer without proper length checking to overwrite memory and cause a segmentation fault, resulting in program termination.

## References
- https://www.exploit-db.com/exploits/47919
- https://www.vulncheck.com/advisories/redir-denial-of-service
- https://github.com/troglobit/redir
