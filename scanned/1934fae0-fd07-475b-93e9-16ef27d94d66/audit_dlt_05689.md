# [?] internal/ethapi: fix panic in accesslist creation (#23225)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-07-28
Source: https://github.com/celo-org/celo-blockchain/commit/2faf796d2a502ef6d3c02681a649bd3f41999ccc
Type: security-commit

## Details
internal/ethapi: fix panic in accesslist creation (#23225)

* internal/ethapi: revert + fix properly in al tracer

* internal/ethapi: use toMessage instead of creating new message

* internal/ethapi: remove ineffassign

* core: fix invalid unmarshalling, fix test

Co-authored-by: Martin Holst Swende <martin@swende.se>
