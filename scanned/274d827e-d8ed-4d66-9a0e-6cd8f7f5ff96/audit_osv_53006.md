# [H] CVE-2022-2601

## Summary
Severity: High
Advisory: CVE-2022-2601
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-2601
Type: osv

## Details
A buffer overflow was found in grub_font_construct_glyph(). A malicious crafted pf2 font can lead to an overflow when calculating the max_glyph_size value, allocating a smaller than needed buffer for the glyph, this further leads to a buffer overflow and a heap based out-of-bounds write. An attacker may use this vulnerability to circumvent the secure boot mechanism.

## References
- https://arstechnica.com/security/2024/08/a-patch-microsoft-spent-2-years-preparing-is-making-a-mess-for-some-linux-users/
- https://security.netapp.com/advisory/ntap-20230203-0004/
- https://security.gentoo.org/glsa/202311-14
- https://bugzilla.redhat.com/show_bug.cgi?id=2112975#c0
