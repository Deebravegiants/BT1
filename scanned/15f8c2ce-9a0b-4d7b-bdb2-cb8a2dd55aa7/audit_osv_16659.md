# [H] CVE-2019-8919

## Summary
Severity: High
Advisory: CVE-2019-8919
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-18
Source: https://osv.dev/vulnerability/CVE-2019-8919
Type: osv

## Details
The seadroid (aka Seafile Android Client) application through 2.2.13 for Android always uses the same Initialization Vector (IV) with Cipher Block Chaining (CBC) Mode to encrypt private data, making it easier to conduct chosen-plaintext attacks or dictionary attacks.

## References
- https://github.com/haiwen/seadroid/issues/789
