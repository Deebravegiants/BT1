# [M] CVE-2017-1000249

## Summary
Severity: Medium
Advisory: CVE-2017-1000249
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-09-11
Source: https://osv.dev/vulnerability/CVE-2017-1000249
Type: osv

## Details
An issue in file() was introduced in commit 9611f31313a93aa036389c5f3b15eea53510d4d1 (Oct 2016) lets an attacker overwrite a fixed 20 bytes stack buffer with a specially crafted .notes section in an ELF binary. This was fixed in commit 35c94dc6acc418f1ad7f6241a6680e5327495793 (Aug 2017).

## References
- http://www.debian.org/security/2017/dsa-3965
- https://security.gentoo.org/glsa/201710-02
- https://github.com/file/file/commit/35c94dc6acc418f1ad7f6241a6680e5327495793
- https://github.com/file/file/commit/9611f31313a93aa036389c5f3b15eea53510d4d
