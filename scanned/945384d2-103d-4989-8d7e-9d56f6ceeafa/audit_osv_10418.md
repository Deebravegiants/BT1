# [H] CVE-2017-15368

## Summary
Severity: High
Advisory: CVE-2017-15368
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2017-15368
Type: osv

## Details
The wasm_dis function in libr/asm/arch/wasm/wasm.c in radare2 2.0.0 allows remote attackers to cause a denial of service (stack-based buffer over-read and application crash) or possibly have unspecified other impact via a crafted WASM file that triggers an incorrect r_hex_bin2str call.

## References
- https://github.com/radare/radare2/commit/52b1526443c1f433087928291d1c3d37a5600515
- https://github.com/radare/radare2/issues/8673
