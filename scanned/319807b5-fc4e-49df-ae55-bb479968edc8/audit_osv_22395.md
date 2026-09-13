# [C] CVE-2022-28550

## Summary
Severity: Critical
Advisory: CVE-2022-28550
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-13
Source: https://osv.dev/vulnerability/CVE-2022-28550
Type: osv

## Details
Matthias-Wandel/jhead jhead 3.06 is vulnerable to Buffer Overflow via shellescape(), jhead.c, jhead. jhead copies strings to a stack buffer when it detects a &i or &o. However, jhead does not check the boundary of the stack buffer. As a result, there will be a stack buffer overflow problem when multiple `&i` or `&o` are given.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/28xxx/CVE-2022-28550.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-28550
- https://github.com/Matthias-Wandel/jhead/issues/51
- https://github.com/Matthias-Wandel/jhead/commit/64894dbc7d8e1e232e85f1cab25c64290b2fc167
