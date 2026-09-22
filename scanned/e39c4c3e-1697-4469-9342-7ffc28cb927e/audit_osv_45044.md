# [M] RSA signature verification raises undocumented exception

## Summary
Severity: Medium
Advisory: OSEC-2026-14
Aliases: CVE-2026-87735
Ecosystem: opam
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/OSEC-2026-14
Type: osv

## Affected
- opam: `mirage-crypto-pk` — affected >=0 <2.3.0, >=0 <a0f59a0c90eb067505b55a03d3bb104eacd6dd33

## Details
The RSA decrypt and encrypt functions raise an Invalid_argument exception if the
message is smaller than 2. This leads to X509 certificates with a signature
value of 0 or 1 to throw this Invalid_argument exception instead of a proper
error.

## Fix

The fix is to reuse the Insufficient_key exception, which is documented and
caught further up in the stack.

## Timeline

- July 28th 2026: report to security@ocaml.org
- August 7th: release of mirage-crypto-pk 2.3.0 and security advisory
