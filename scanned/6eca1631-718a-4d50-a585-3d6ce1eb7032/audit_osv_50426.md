# [M] CVE-2020-15709

## Summary
Severity: Medium
Advisory: CVE-2020-15709
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-09-05
Source: https://osv.dev/vulnerability/CVE-2020-15709
Type: osv

## Details
Versions of add-apt-repository before 0.98.9.2, 0.96.24.32.14, 0.96.20.10, and 0.92.37.8ubuntu0.1~esm1, printed a PPA (personal package archive) description to the terminal as-is, which allowed PPA owners to provide ANSI terminal escapes to modify terminal contents in unexpected ways.

## References
- https://git.launchpad.net/software-properties/commit/add-apt-repository?id=97e2fe7d181e8711e0f5253d3b8db40426c17f1e
