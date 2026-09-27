# [C] CVE-2025-29366

## Summary
Severity: Critical
Advisory: CVE-2025-29366
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-29366
Type: osv

## Details
In mupen64plus v2.6.0 there is an array overflow vulnerability in the write_rdram_regs and write_rdram_regs functions, which enables executing arbitrary commands on the host machine.

## References
- https://github.com/mupen64plus/mupen64plus-core/blob/master/src/device/rdram/rdram.h#L50
- https://github.com/mupen64plus/mupen64plus-core/blob/master/src/device/rdram/rdram.h#L60
- https://gist.github.com/Giles-one/f4ea405c2a26000bb4ff4cfb9622be49
- https://github.com/Giles-one/mupen64plusEscape/tree/main/BUG1
- https://github.com/mupen64plus/mupen64plus-core/blob/2.6.0/src/device/rdram/rdram.c#L159
