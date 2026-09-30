# [M] Inter-Blockchain Communication (IBC) protocol "Huckleberry" vulnerability in github.com/cosmos/ibc-go

## Summary
Severity: Medium
Advisory: GO-2024-2874
Aliases: GHSA-qjcv-rx3v-7mvj
Package: github.com/cosmos/ibc-go
Published: 2024-05-23
Source: https://osv.dev/vulnerability/GO-2024-2874
Type: chain-advisory

## Affected
- Go: `github.com/cosmos/ibc-go` — affected unspecified
- Go: `github.com/cosmos/ibc-go/v2` — affected unspecified
- Go: `github.com/cosmos/ibc-go/v3` — affected unspecified
- Go: `github.com/cosmos/ibc-go/v4` — affected unspecified
- Go: `github.com/cosmos/ibc-go/v5` — affected unspecified
- Go: `github.com/cosmos/ibc-go/v6` — affected unspecified
- Go: `github.com/cosmos/ibc-go/v7` — affected >=0 <7.0.1

## Details
The ibc-go module is affected by the Inter-Blockchain Communication (IBC) protocol "Huckleberry" vulnerability. The vulnerability allowed an attacker to send arbitrary transactions onto target chains and trigger arbitrary state transitions, including but not limited to, theft of funds. It was possible to exploit this vulnerability in specific situations involving relaying packets in which the source chain is also the final destination chain. Affected networks are those that allow for fee grant capabilities and use a native Relayer (e.g., Osmosis and Juno).

## References
- https://github.com/cosmos/ibc-go/commit/c77f80f812940fe3b93980d13a5cdd6980e907cc
- https://github.com/cosmos/ibc-go/issues/1532
