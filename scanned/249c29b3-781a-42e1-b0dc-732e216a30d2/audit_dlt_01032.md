# [H] Cosmos packet-forward-middleware vulnerable to chain-halt

## Summary
Severity: High
Chain: github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v4
Component: github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v4, github.com/cosmos/ibc-apps/middleware/packet-forward
Published: 2023-10-26
Source: https://github.com/advisories/GHSA-w6rp-vxj2-fjhr
Type: github-advisory

## Details
The Cosmos SDK is used for Inter-Blockchain Communication Protocol (IBC) applications and middleware. The [packet-forward-middleware](https://github.com/cosmos/ibc-apps/tree/main/middleware/packet-forward-middleware) module is an IBC middleware module built for Cosmos blockchains utilizing the IBC protocol allowing routing of incoming IBC packets from a source chain to a destination chain. The `packet-forward-middleware` module is vulnerable to potential chain-halt due to error non-determinism.

### Patches
Please patch at your earliest convenience by applying one of the following patch versions, respective to the chain's ibc-go major version:
v4.1.1
v5.2.1
v6.1.1
