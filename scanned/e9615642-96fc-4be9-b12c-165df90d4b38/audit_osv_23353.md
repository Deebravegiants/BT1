# [C] CVE-2022-48317

## Summary
Severity: Critical
Advisory: CVE-2022-48317
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-48317
Type: osv

## Details
Expired sessions were not securely terminated in the RestAPI for Tribe29's Checkmk <= 2.1.0p10 and Checkmk <= 2.0.0p28 allowing an attacker to use expired session tokens when communicating with the RestAPI.

## References
- https://checkmk.com/werk/14485
