# [M] Denial of service via malformed size parameters in github.com/ipfs/go-bitfield

## Summary
Severity: Medium
Advisory: GO-2023-1558
Aliases: CVE-2023-23626, GHSA-2h6c-j3gf-xp9r
Package: github.com/ipfs/go-bitfield
Published: 2023-02-14
Source: https://osv.dev/vulnerability/GO-2023-1558
Type: chain-advisory

## Affected
- Go: `github.com/ipfs/go-bitfield` — affected >=0 <1.1.0

## Details
When feeding untrusted user input into the size parameter of NewBitfield and FromBytes functions, an attacker can trigger panics.

This happens when the size is a not a multiple of 8 or is negative.

A workaround is to ensure size%8 == 0 && size >= 0 yourself before calling NewBitfield or FromBytes.

## References
- https://github.com/ipfs/go-bitfield/security/advisories/GHSA-2h6c-j3gf-xp9r
- https://github.com/ipfs/go-bitfield/commit/5e1d256fe043fc4163343ccca83862c69c52e579
