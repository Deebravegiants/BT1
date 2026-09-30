# [H] CVE-2021-30462

## Summary
Severity: High
Advisory: CVE-2021-30462
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-30462
Type: osv

## Details
VestaCP through 0.9.8-24 allows the admin user to escalate privileges to root because the Sudo configuration does not require a password to run /usr/local/vesta/bin scripts.

## References
- https://ssd-disclosure.com/ssd-advisory-vestacp-lpe-vulnerabilities/
