# [?] Fix nil pointer dereference in validator client with non-Prysm beacon-nodes (#16449)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-03-02
Source: https://github.com/OffchainLabs/prysm/commit/544bc3eb45cdddeb791c44b5b27b40670bbf8abf
Type: security-commit

## Details
Fix nil pointer dereference in validator client with non-Prysm beacon-nodes (#16449)

1. When connecting to a REST-only beacon node (e.g. Teku, Lighthouse),
the gRPC connection provider is nil. The grpcClientManager was
unconditionally calling ConnectionCounter() on the provider in both
newGrpcClientManager and getClient, causing a SIGSEGV panic on startup.
2. runner.go — Made initial PushProposerSettings non-fatal. Lighthouse
returns 500: UnableToReadSlot on
/eth/v1/validator/prepare_beacon_proposer at genesis (slot 0) before any
blocks exist. The run loop already handles this as a warning — now the
initial call does too, and it retries on the next slot.


to repro the bug:
```yaml
participants:
  - el_type: geth
    el_image: ethpandaops/geth:master
    cl_type: prysm
    cl_image: ethpandaops/prysm-beacon-chain:develop
    vc_type: prysm
    vc_image: ethpandaops/prysm-validator:develop
    count: 1
  - el_type: geth
    el_image: ethpandaops/geth:master
    cl_type: teku
    cl_image: ethpandaops/teku:master
    vc_type: prysm
    vc_image: ethpandaops/prysm-validator:develop
    count: 1
additional_services:
  - dora
```

To repro the fix: 
```yaml
participants:
  - el_type: geth
```

_Trimmed to 38 lines — full report: https://github.com/OffchainLabs/prysm/commit/544bc3eb45cdddeb791c44b5b27b40670bbf8abf_
