# [M] CVE-2022-48319

## Summary
Severity: Medium
Advisory: CVE-2022-48319
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-48319
Type: osv

## Details
Sensitive host secret disclosed in cmk-update-agent.log file in Tribe29's Checkmk <= 2.1.0p13, Checkmk <= 2.0.0p29, and all versions of Checkmk 1.6.0 (EOL) allows an attacker to gain access to the host secret through the unprotected agent updater log file.

## References
- https://checkmk.com/werk/14916
