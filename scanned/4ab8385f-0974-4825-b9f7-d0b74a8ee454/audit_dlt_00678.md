# [?] discovery: fix panic in DNS fallback SRV lookup

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-06-19
Source: https://github.com/lightningnetwork/lnd/commit/2a3642c691e08c2115f9177251bb9cbeed5f0a6a
Type: security-commit

## Details
discovery: fix panic in DNS fallback SRV lookup

The fallback SRV lookup type-asserted each DNS Answer record to *dns.SRV
unconditionally. If the response contains a non-SRV record (e.g. an A or
CNAME), the type assertion panics and crashes the daemon. Use the
comma-ok form to skip non-SRV records instead.

Also guard against an empty LookupHost result for the shim, which would
otherwise panic on an out-of-bounds index into addrs.

This is safe to discuss and fix in public. The bug is very unlikely to be
exploitable: triggering it requires either a DNS seeder to serve a
malformed response, or an on-path MITM injecting one (the fallback
response is unauthenticated). A malicious seeder already has far more
direct ways to disrupt a node, and a MITM attack is hard to mount, so the
panic does not meaningfully widen the attack surface.
