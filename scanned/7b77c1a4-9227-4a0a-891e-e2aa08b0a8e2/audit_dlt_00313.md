# [H] EL-2026-28: NEW_POOLED_TRANSACTION_HASHES_66 causes OOM

## Summary
Severity: High
Chain: Ethereum (execution layer)
Component: Erigon
Source: https://notes.ethereum.org/Ta8bupLNRZukrFQb25oDDw
Type: ef-disclosure

## Details
## Short description
A malicious peer can send an oversized NEW_POOLED_TRANSACTION_HASHES_66 message advertising ~40 million hashes, forcing the node to allocate ~1.22 GiB of memory without validation and causing OOM crashes.

## Attack scenario
1. Attacker opens devp2p connection (ETH/66)
2. Sends 1.24 GiB NEW_POOLED_TRANSACTION_HASHES_66 frame (40,000,000 × 33 bytes)
3. Victim's `(*Fetch).handleInboundMessage` allocates 1.22 GiB instantly
4. RSS jumps to ~1.2 GiB, exceeding 1 GB soft limit - process killed by OOM

## Impact
- **Node crash**: Single packet triggers OOM
- **Network disruption**: Simultaneous attacks knock out infrastructure nodes
- **Validator penalties**: Missed attestations/proposals during crashes

## Components
**File**: `txnprovider/txpool/fetch.go`
**Function**: `(*Fetch).handleInboundMessage`
**Vulnerable code**:
```go
hashCount, pos, err := ParseHashesCount(req.Data, 0)
hashes := make([]byte, 32*hashCount)  // Unbounded allocation
```

Related functions:
- `ParseHashesCount` - returns unbounded count
- `FilterKnownIdHashes` - processes after allocation

## Reproduction
The vulnerability can be reproduced using the provided test cases.

**Test File Location**: `tests/txpool/dos_hash_allocation_test.go`

**Test Commands**:
```bash
# Run main PoC test
go test -v ./tests/txpool -run TestE2E_DoS_HashAllocation -timeout 30s

# Run sustained attack test
```

_Trimmed to 38 lines — full report: https://notes.ethereum.org/Ta8bupLNRZukrFQb25oDDw_
