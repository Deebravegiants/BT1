# [M] CVE-2023-1768

## Summary
Severity: Medium
Advisory: CVE-2023-1768
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-04-04
Source: https://osv.dev/vulnerability/CVE-2023-1768
Type: osv

## Details
Inappropriate error handling in Tribe29 Checkmk <= 2.1.0p25, <= 2.0.0p34, <= 2.2.0b3 (beta), and all versions of Checkmk 1.6.0 causes the symmetric encryption of agent data to fail silently and transmit the data in plaintext in certain configurations.

## References
- https://checkmk.com/werk/15423
