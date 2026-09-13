# [H] staging: ks7010: potential buffer overflow in ks_wlan_set_encode_ext()

## Summary
Severity: High
Advisory: CVE-2023-53554
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53554
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.253, >=5.5.0 <5.10.190, >=5.11.0 <5.15.124, >=5.16.0 <6.1.43, >=6.2.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: ks7010: potential buffer overflow in ks_wlan_set_encode_ext()

The "exc->key_len" is a u16 that comes from the user.  If it's over
IW_ENCODING_TOKEN_MAX (64) that could lead to memory corruption.

## References
- https://git.kernel.org/stable/c/5373a1aa91b2298f9305794b8270cf9896be96b6
- https://git.kernel.org/stable/c/5f1c7031e044cb2fba82836d55cc235e2ad619dc
- https://git.kernel.org/stable/c/663fff29fd613e2b0d30c4138157312ba93c4939
- https://git.kernel.org/stable/c/7ae9f55a495077f838bab466411ee6f38574df9b
- https://git.kernel.org/stable/c/9496fb96ddeb740dc6b966f4a7d8dfb8b93921c6
- https://git.kernel.org/stable/c/b1b04b56745bc79286c80aa876fabfab1e08ebf1
- https://git.kernel.org/stable/c/baf420e30364ef9efe3e29a5c0e01e612aebf3fe
- https://git.kernel.org/stable/c/caac4b6c15b66feae4d83f602e1e46f124540202
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53554.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53554
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
