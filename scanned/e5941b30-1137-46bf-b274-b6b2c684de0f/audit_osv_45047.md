# [M] Timing leak in NIST elliptic curves scalar multiplication

## Summary
Severity: Medium
Advisory: OSEC-2026-17
Aliases: CVE-2026-87737
Ecosystem: opam
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/OSEC-2026-17
Type: osv

## Affected
- opam: `mirage-crypto-ec` — affected >=0.11.3 <2.4.0, >=0 <1a61aeee7f593ec067612df1739ec905eab0450f

## Details
The scalar multiplication includes pre-computed tables for speedup (introduced in mirage-crypto-ec 0.11.3). The lookup algorithm for these tables performs secret-dependent reads instead of scanning the entire table.

## Solution

Instead of using the index `n - 1`, where `n` is secret-dependent, use `i - 1`, as done in the Go reference implementation. If `n` is 0, there is a out-of-bounds read before the patch.

## Timeline
- 2026-08-12: report by Eric Ebinger to security@ocaml.org
- 2026-08-17: release of mirage-crypto-ec 2.4.0 and this advisory
