# [M] JLSEC-2026-97

## Summary
Severity: Medium
Advisory: JLSEC-2026-97
Ecosystem: Julia
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/JLSEC-2026-97
Type: osv

## Affected
- Julia: `Wayland_jll` — affected >=0 <1.21.0+0

## Details
An internal reference count is held on the buffer pool, incremented every time a new buffer is created from the pool. The reference count is maintained as an int; on LP64 systems this can cause the reference count to overflow if the client creates a large number of `wl_shm` buffer objects, or if it can coerce the server to create a large number of external references to the buffer storage. With the reference count overflowing, a use-after-free can be constructed on the `wl_shm_pool` tracking structure, where values may be incremented or decremented; it may also be possible to construct a limited oracle to leak 4 bytes of server-side memory to the attacking client at a time.

## References
- https://gitlab.freedesktop.org/wayland/wayland/-/issues/224
