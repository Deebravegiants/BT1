# [H] JLSEC-2026-472

## Summary
Severity: High
Advisory: JLSEC-2026-472
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-472
Type: osv

## Affected
- Julia: `Xorg_libX11_jll` — affected >=0 <1.8.6+0

## Details
A vulnerability was found in libX11. The security flaw occurs because the functions in `src/InitExt.c` in libX11 do not check that the values provided for the Request, Event, or Error IDs are within the bounds of the arrays that those functions write to, using those IDs as array indexes. They trust that they were called with values provided by an Xserver adhering to the bounds specified in the X11 protocol, as all X servers provided by X.Org do. As the protocol only specifies a single byte for these values, an out-of-bounds value provided by a malicious server (or a malicious proxy-in-the-middle) can only overwrite other portions of the Display structure and not write outside the bounds of the Display structure itself, possibly causing the client to crash with this memory corruption.

## References
- https://access.redhat.com/security/cve/CVE-2023-3138
- https://gitlab.freedesktop.org/xorg/lib/libx11/-/commit/304a654a0d57bf0f00d8998185f0360332cfa36c
- https://lists.x.org/archives/xorg-announce/2023-June/003406.html
- https://lists.x.org/archives/xorg-announce/2023-June/003407.html
- https://security.netapp.com/advisory/ntap-20231208-0008/
