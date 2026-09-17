# [H] CVE-2013-7469

## Summary
Severity: High
Advisory: CVE-2013-7469
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-21
Source: https://osv.dev/vulnerability/CVE-2013-7469
Type: osv

## Details
Seafile through 6.2.11 always uses the same Initialization Vector (IV) with Cipher Block Chaining (CBC) Mode to encrypt private data, making it easier to conduct chosen-plaintext attacks or dictionary attacks.

## References
- https://drive.google.com/file/d/1rwYsnuhZZxmSR6Zs8rJlWW3R27XBOSJU/view
- https://github.com/haiwen/seafile/issues/350
