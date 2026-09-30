# [H] fbcon: fix integer overflow in fbcon_do_set_font

## Summary
Severity: High
Advisory: CVE-2025-39967
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39967
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.300, >=5.5.0 <5.10.245, >=5.9.0 <5.15.194, >=5.11.0 <6.1.155, >=5.16.0 <6.6.109, >=6.2.0 <6.12.50, >=6.7.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbcon: fix integer overflow in fbcon_do_set_font

Fix integer overflow vulnerabilities in fbcon_do_set_font() where font
size calculations could overflow when handling user-controlled font
parameters.

The vulnerabilities occur when:
1. CALC_FONTSZ(h, pitch, charcount) performs h * pith * charcount
   multiplication with user-controlled values that can overflow.
2. FONT_EXTRA_WORDS * sizeof(int) + size addition can also overflow
3. This results in smaller allocations than expected, leading to buffer
   overflows during font data copying.

Add explicit overflow checking using check_mul_overflow() and
check_add_overflow() kernel helpers to safety validate all size
calculations before allocation.

## References
- https://git.kernel.org/stable/c/1a194e6c8e1ee745e914b0b7f50fa86c89ed13fe
- https://git.kernel.org/stable/c/4a4bac869560f943edbe3c2b032062f6673b13d3
- https://git.kernel.org/stable/c/994bdc2d23c79087fbf7dcd9544454e8ebcef877
- https://git.kernel.org/stable/c/9c8ec14075c5317edd6b242f1be8167aa1e4e333
- https://git.kernel.org/stable/c/a6eb9f423b3db000aaedf83367b8539f6b72dcfc
- https://git.kernel.org/stable/c/adac90bb1aaf45ca66f9db8ac100be16750ace78
- https://git.kernel.org/stable/c/b8a6e85328aeb9881531dbe89bcd2637a06c3c95
- https://git.kernel.org/stable/c/c0c01f9aa08c8e10e10e8c9ebb5be01a4eff6eb7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39967.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39967
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
