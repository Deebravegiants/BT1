# [H] CVE-2020-27511

## Summary
Severity: High
Advisory: CVE-2020-27511
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-21
Source: https://osv.dev/vulnerability/CVE-2020-27511
Type: osv

## Details
An issue was discovered in the stripTags and unescapeHTML components in Prototype 1.7.3 where an attacker can cause a Regular Expression Denial of Service (ReDOS) through stripping crafted HTML tags.

## References
- http://prototypejs.org/
- https://github.com/prototypejs/prototype/blob/dee2f7d8611248abce81287e1be4156011953c90/src/prototype/lang/string.js#L283
- https://github.com/yetingli/PoCs/blob/main/CVE-2020-27511/Prototype.md
