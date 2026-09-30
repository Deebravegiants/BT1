# [C] Read-only volume remount bypass via guest CAP_SYS_ADMIN

## Summary
Severity: Critical
Advisory: RUSTSEC-2026-0147
Aliases: CVE-2026-46695, GHSA-g6ww-w5j2-r7x3, GO-2026-5392, PYSEC-2026-299
Ecosystem: crates.io
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-16
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0147
Type: osv

## Affected
- crates.io: `boxlite` — affected >=0.0.0-0 <0.9.0

## Details
Affected versions of `boxlite` mount host directories shared via virtiofs
as guest-side read-only by setting `MS_RDONLY` from the guest. Because the
default guest capability set included `CAP_SYS_ADMIN`, untrusted code
running inside a sandbox could execute `mount -o remount,rw <path>` to
re-flag the share as read-write and then write through to the host
filesystem — fully escaping the read-only contract `boxlite` advertised
to callers.

The fix in v0.9.0 enforces read-only at the hypervisor level via
`krun_add_virtiofs3` (so the guest's `MS_RDONLY` is no longer the
authoritative gate) and drops `CAP_SYS_ADMIN` from the default guest
capability set (matching Docker's defaults).

This is a sandbox-escape bug: `boxlite` is a sandboxing runtime, so the
read-only invariant is part of its security contract. CVSS rated 10.0 by
the upstream advisory.

## References
- https://crates.io/crates/boxlite
- https://rustsec.org/advisories/RUSTSEC-2026-0147.html
- https://github.com/boxlite-ai/boxlite/security/advisories/GHSA-g6ww-w5j2-r7x3
- https://github.com/boxlite-ai/boxlite/pull/454
