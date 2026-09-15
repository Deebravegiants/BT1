# [H] CVE-2021-45099

## Summary
Severity: High
Advisory: CVE-2021-45099
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-16
Source: https://osv.dev/vulnerability/CVE-2021-45099
Type: osv

## Details
The addon.stdin service in addon-ssh (aka Home Assistant Community Add-on: SSH & Web Terminal) before 10.0.0 has an attack surface that requires social engineering. NOTE: the vendor does not agree that this is a vulnerability; however, addon.stdin was removed as a defense-in-depth measure against complex social engineering situations

## References
- https://github.com/hassio-addons/addon-ssh/releases/tag/v10.0.0
- https://gist.github.com/Eriner/0872628519f70556d2c26c83439a9f67
