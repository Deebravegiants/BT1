# [M] CVE-2021-47611

## Summary
Severity: Medium
Advisory: CVE-2021-47611
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47611
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac80211: validate extended element ID is present

Before attempting to parse an extended element, verify that
the extended element ID is present.

## References
- https://git.kernel.org/stable/c/7fd214fc7f2ee3a89f91e717e3cfad55f5a27045
- https://git.kernel.org/stable/c/a19cf6844b509d44ecbd536f33d314d91ecdd2b5
- https://git.kernel.org/stable/c/c62b16f98688ae7bc0ab23a6490481f4ce9b3a49
- https://git.kernel.org/stable/c/03029bb044ccee60adbc93e70713f3ae58abc3a1
- https://git.kernel.org/stable/c/768c0b19b50665e337c96858aa2b7928d6dcf756
