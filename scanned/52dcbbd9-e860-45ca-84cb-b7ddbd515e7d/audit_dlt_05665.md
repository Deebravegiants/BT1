# [?] Address cargo audit failure `RUSTSEC-2024-0437` (#7114)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-03-13
Source: https://github.com/sigp/lighthouse/commit/3a555f571f622979ff322290b0bf3ebd6e265489
Type: security-commit

## Details
Address cargo audit failure `RUSTSEC-2024-0437` (#7114)

Resolves #7091


  The `prometheus` crate pulls in `protobuf 2.x` which fails cargo audit. We actually dont use any `protobuf` related features in LH. By disabling default features for `prometheus`, we no longer pull in the `protobuf` crate
