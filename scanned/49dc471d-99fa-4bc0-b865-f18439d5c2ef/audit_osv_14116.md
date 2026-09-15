# [H] CVE-2018-7304

## Summary
Severity: High
Advisory: CVE-2018-7304
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-21
Source: https://osv.dev/vulnerability/CVE-2018-7304
Type: osv

## Details
Tiki 17.1 does not validate user input for special characters; consequently, a CSV Injection attack can open a CMD.EXE or Calculator window on the victim machine to perform malicious activity, as demonstrated by an "=cmd|' /C calc'!A0" payload during User Creation.

## References
- https://websecnerd.blogspot.in/2018/01/tiki-wiki-cms-groupware-17.html
