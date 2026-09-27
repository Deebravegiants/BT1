# [M] CVE-2021-3731

## Summary
Severity: Medium
Advisory: CVE-2021-3731
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3731
Type: osv

## Details
LedgerSMB does not sufficiently guard against being wrapped by other sites, making it vulnerable to 'clickjacking'. This allows an attacker to trick a targetted user to execute unintended actions.

## References
- https://huntr.dev/bounties/5664331d-f5f8-4412-8566-408f8655888a
- https://ledgersmb.org/cve-2021-3731-clickjacking
- https://www.debian.org/security/2021/dsa-4962
