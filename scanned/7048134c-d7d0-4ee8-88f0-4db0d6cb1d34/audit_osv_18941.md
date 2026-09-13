# [C] CVE-2020-5235

## Summary
Severity: Critical
Advisory: CVE-2020-5235
Aliases: GHSA-gcx3-7m76-287p
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-04
Source: https://osv.dev/vulnerability/CVE-2020-5235
Type: osv

## Details
There is a potentially exploitable out of memory condition In Nanopb before 0.4.1, 0.3.9.5, and 0.2.9.4. When nanopb is compiled with PB_ENABLE_MALLOC, the message to be decoded contains a repeated string, bytes or message field and realloc() runs out of memory when expanding the array nanopb can end up calling `free()` on a pointer value that comes from uninitialized memory. Depending on platform this can result in a crash or further memory corruption, which may be exploitable in some cases. This problem is fixed in nanopb-0.4.1, nanopb-0.3.9.5, nanopb-0.2.9.4.

## References
- https://github.com/nanopb/nanopb/commit/45582f1f97f49e2abfdba1463d1e1027682d9856
- https://github.com/nanopb/nanopb/commit/7b396821ddd06df8e39143f16e1dc0a4645b89a3
- https://github.com/nanopb/nanopb/commit/aa9d0d1ca78d6adec3adfeecf3a706c7f9df81f2
- https://github.com/nanopb/nanopb/security/advisories/GHSA-gcx3-7m76-287p
