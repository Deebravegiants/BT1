# [H] CVE-2021-47288

## Summary
Severity: High
Advisory: CVE-2021-47288
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47288
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: ngene: Fix out-of-bounds bug in ngene_command_config_free_buf()

Fix an 11-year old bug in ngene_command_config_free_buf() while
addressing the following warnings caught with -Warray-bounds:

arch/alpha/include/asm/string.h:22:16: warning: '__builtin_memcpy' offset [12, 16] from the object at 'com' is out of the bounds of referenced subobject 'config' with type 'unsigned char' at offset 10 [-Warray-bounds]
arch/x86/include/asm/string_32.h:182:25: warning: '__builtin_memcpy' offset [12, 16] from the object at 'com' is out of the bounds of referenced subobject 'config' with type 'unsigned char' at offset 10 [-Warray-bounds]

The problem is that the original code is trying to copy 6 bytes of
data into a one-byte size member _config_ of the wrong structue
FW_CONFIGURE_BUFFERS, in a single call to memcpy(). This causes a
legitimate compiler warning because memcpy() overruns the length
of &com.cmd.ConfigureBuffers.config. It seems that the right
structure is FW_CONFIGURE_FREE_BUFFERS, instead, because it contains
6 more members apart from the header _hdr_. Also, the name of
the function ngene_command_config_free_buf() suggests that the actual
intention is to ConfigureFreeBuffers, instead of ConfigureBuffers
(which takes place in the function ngene_command_config_buf(), above).

Fix this by enclosing those 6 members of struct FW_CONFIGURE_FREE_BUFFERS
into new struct config, and use &com.cmd.ConfigureFreeBuffers.config as
the destination address, instead of &com.cmd.ConfigureBuffers.config,
when calling memcpy().

This also helps with the ongoing efforts to globally enable
-Warray-bounds and get us closer to being able to tighten the
FORTIFY_SOURCE routines on memcpy().

## References
- https://git.kernel.org/stable/c/e991457afdcb5f4dbc5bc9d79eaf775be33e7092
- https://git.kernel.org/stable/c/ec731c6ef564ee6fc101fc5d73e3a3a953d09a00
- https://git.kernel.org/stable/c/4487b968e5eacd02c493303dc2b61150bb7fe4b2
- https://git.kernel.org/stable/c/8d4abca95ecc82fc8c41912fa0085281f19cc29f
- https://git.kernel.org/stable/c/b9a178f189bb6d75293573e181928735f5e3e070
- https://git.kernel.org/stable/c/c6ddeb63dd543b5474b0217c4e47538b7ffd7686
- https://git.kernel.org/stable/c/e617fa62f6cf859a7b042cdd6c73af905ff8fca3
- https://git.kernel.org/stable/c/e818f2ff648581a6c553ae2bebc5dcef9a8bb90c
