# [C] sctp: add INIT verification after cookie unpacking

## Summary
Severity: Critical
Advisory: CVE-2026-72398
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72398
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: add INIT verification after cookie unpacking

In SCTP handshake, the INIT chunk is initially processed by the server
and embedded into the cookie carried in INIT-ACK. The client then
returns this cookie via COOKIE-ECHO, where the server unpacks it and
reconstructs the original INIT chunk.

When cookie authentication is enabled, the cookie contents are protected
against tampering, so reusing the unpacked INIT without re-verification
is safe.

However, when cookie authentication is disabled, the reconstructed INIT
can no longer be trusted. In this case, the INIT must be explicitly
validated after unpacking to avoid processing potentially tampered data.

Add sctp_verify_init() checks after cookie unpacking in COOKIE-ECHO
processing paths (sctp_sf_do_5_1D_ce() and sctp_sf_do_5_2_4_dupcook())
when cookie_auth_enable is disabled. On failure, the new association is
freed and the packet is discarded.

Also tighten cookie validation in sctp_unpack_cookie() by verifying the
embedded chunk type is SCTP_CID_INIT before treating it as an INIT
chunk.

Finally, update sctp_verify_init() to validate parameter bounds using
the actual embedded INIT length instead of chunk->chunk_end, since the
INIT stored in COOKIE-ECHO may not span the entire chunk buffer.

## References
- https://git.kernel.org/stable/c/062bcbf8d1f1051fdeb20b94920031b0e2cb95a2
- https://git.kernel.org/stable/c/414c5447fe6a200613dd46d7fdc8454622076cb1
- https://git.kernel.org/stable/c/bca3100f550281c2f2418652338bced3b35af0e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72398.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72398
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
