# [C] cifs: potential buffer overflow in handling symlinks

## Summary
Severity: Critical
Advisory: CVE-2022-49058
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49058
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.239, >=4.20.0 <5.4.190, >=5.5.0 <5.10.112, >=5.11.0 <5.15.35, >=5.16.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: potential buffer overflow in handling symlinks

Smatch printed a warning:
	arch/x86/crypto/poly1305_glue.c:198 poly1305_update_arch() error:
	__memcpy() 'dctx->buf' too small (16 vs u32max)

It's caused because Smatch marks 'link_len' as untrusted since it comes
from sscanf(). Add a check to ensure that 'link_len' is not larger than
the size of the 'link_str' buffer.

## References
- https://git.kernel.org/stable/c/1316c28569a80ab3596eeab05bf5e01991e7e739
- https://git.kernel.org/stable/c/22d658c6c5affed10c8907e67160cef0b6c92186
- https://git.kernel.org/stable/c/3e582749e742e662a8e9bb37cffac62dccaaa1e2
- https://git.kernel.org/stable/c/4e166a41180be2f1e66bbb6d46448e80a9a5ec05
- https://git.kernel.org/stable/c/515e7ba11ef043d6febe69389949c8ef5f25e9d0
- https://git.kernel.org/stable/c/64c4a37ac04eeb43c42d272f6e6c8c12bfcf4304
- https://git.kernel.org/stable/c/9901b07ba42b39266b34a888e48d7306fd707bee
- https://git.kernel.org/stable/c/eb5f51756944735ac70cd8bb38637cc202e29c91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49058.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49058
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
