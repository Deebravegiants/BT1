# [M] CVE-2020-10966

## Summary
Severity: Medium
Advisory: CVE-2020-10966
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-10966
Type: osv

## Details
In the Password Reset Module in VESTA Control Panel through 0.9.8-25 and Hestia Control Panel before 1.1.1, Host header manipulation leads to account takeover because the victim receives a reset URL containing an attacker-controlled server name.

## References
- https://github.com/hestiacp/hestiacp/releases/tag/1.1.1
- https://github.com/serghey-rodin/vesta/commit/c3c4de43d6701560f604ca7996f717b08e3d7d1d
- https://github.com/hestiacp/hestiacp/issues/748
