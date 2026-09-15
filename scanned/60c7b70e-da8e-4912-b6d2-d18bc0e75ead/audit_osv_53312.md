# [H] CVE-2022-3775

## Summary
Severity: High
Advisory: CVE-2022-3775
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-12-19
Source: https://osv.dev/vulnerability/CVE-2022-3775
Type: osv

## Details
When rendering certain unicode sequences, grub2's font code doesn't proper validate if the informed glyph's width and height is constrained within bitmap size. As consequence an attacker can craft an input which will lead to a out-of-bounds write into grub2's heap, leading to memory corruption and availability issues. Although complex, arbitrary code execution could not be discarded.

## References
- https://security.gentoo.org/glsa/202311-14
- https://access.redhat.com/security/cve/cve-2022-3775
