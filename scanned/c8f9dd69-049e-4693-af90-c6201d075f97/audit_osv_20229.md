# [M] CVE-2021-3236

## Summary
Severity: Medium
Advisory: CVE-2021-3236
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/CVE-2021-3236
Type: osv

## Details
vim 8.2.2348 is affected by null pointer dereference, allows local attackers to cause a denial of service (DoS) via the ex_buffer_all method.

## References
- https://security.netapp.com/advisory/ntap-20230915-0001/
- https://github.com/vim/vim/issues/7674
