# [M] CVE-2020-10870

## Summary
Severity: Medium
Advisory: CVE-2020-10870
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-23
Source: https://osv.dev/vulnerability/CVE-2020-10870
Type: osv

## Details
Zim through 0.72.1 creates temporary directories with predictable names. A malicious user could predict and create Zim's temporary directories and prevent other users from being able to start Zim, resulting in a denial of service.

## References
- https://github.com/zim-desktop-wiki/zim-desktop-wiki/issues/1028
