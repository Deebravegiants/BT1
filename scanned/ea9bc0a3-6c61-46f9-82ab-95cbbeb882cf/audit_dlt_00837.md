# [?] Invent "noncritical params" for Simplex timing & DoS protection params

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2026-03-25
Source: https://github.com/ton-blockchain/ton/commit/2e4585f5045c1993e02c482d3bb768a9ce04e688
Type: security-commit

## Details
Invent "noncritical params" for Simplex timing & DoS protection params

The idea is to allow overriding these parameters from the engine console
if we need to do a manual recovery.

The commit allows these noncritical parameters to be set from config (we
expect to use this mainly for target_block_rate) and from validator
options.
