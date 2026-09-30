# [C] CVE-2023-40359

## Summary
Severity: Critical
Advisory: CVE-2023-40359
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-14
Source: https://osv.dev/vulnerability/CVE-2023-40359
Type: osv

## Details
xterm before 380 supports ReGIS reporting for character-set names even if they have unexpected characters (i.e., neither alphanumeric nor underscore), aka a pointer/overflow issue. This can only occur for xterm installations that are configured at compile time to use a certain experimental feature.

## References
- https://invisible-island.net/xterm/xterm.log.html#xterm_380
