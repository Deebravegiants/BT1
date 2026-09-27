# [H] CVE-2021-42719

## Summary
Severity: High
Advisory: CVE-2021-42719
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-42719
Type: osv

## Details
Adobe Bridge version 11.1.1 (and earlier) is affected by an out-of-bounds read vulnerability when parsing a crafted .jpe file, which could result in a read past the end of an allocated memory structure. An attacker could leverage this vulnerability to execute code in the context of the current user. Exploitation of this issue requires user interaction in that a victim must open a malicious file.

## References
- https://helpx.adobe.com/security/products/bridge/apsb21-94.html
