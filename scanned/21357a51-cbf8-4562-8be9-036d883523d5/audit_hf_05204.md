# [H] Potential Divergence Between Off-Chainand On-Chain Poseidon Hashing Causes Unslashable RLN Identities

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23333
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The PoseidonHasher contract initializes the Poseidon state using a raw EVM addition:
let s1 := add(input, C1)
The Yul add instruction wraps modulo 2ˆ256, not modulo the BN254 field prime Q. As a result, the effective input
absorbed into the Poseidon permutation becomes:
s1_effective = ((input + C1) mod 2^256) mod Q
However, canonical Poseidon implementations used in RLN circuits and off-chain tooling interpret inputs as field
elements:
s1_canonical = ( (input mod Q) + C1 ) mod Q = (input + C1) mod Q
These two differ whenever input + C1 2ˆ256. This only occurs for inputs in the range:
input [2^256 C1, 2^256)
If off-chain code uses canonical field arithmetic (as typical Poseidon libraries do) while the on-chain hasher uses
this wraparound behavior, the two commitments diverge.
In the StatusL2 RLN implementation, this inconsistency affects slashing:
• A user registers with an identity commitment computed off-chain.
• During slash, the contract recomputes the commitment on-chain using this hasher.
• If the two computations do not match, slash reverts with RLN__MemberNotFound(), making that identity
unslashable.
This only becomes reachable if RLN private keys are treated as arbitrary bytes32 rather than constrained to the
BN254 scalar field (< Q). If the protocol correctly samples keys in Fr, the overflow path is unreachable.

## Proof of Concept
```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;
import { Test } from "forge-std/Test.sol";
import { PoseidonHasher } from "../src/rln/PoseidonHasher.sol";
contract PoseidonHasherTest is Test {
    PoseidonHasher public hasher;
    function setUp() public {
        hasher = new PoseidonHasher();
    }
    function test_PoCHashMaxUint() public {
        uint256 input = type(uint256).max;
        // Expected hash from circomlibjs (which handles field arithmetic correctly)
        uint256 expected =
            11254588113248280256028662529799552354366536761492627237202955510067774853962;,!
        uint256 result = hasher.hash(input);
        assertNotEq(result, expected, "Hash mismatch for max uint256 (Overflow issue)");
    }
}
```
• Output:
Ran 1 test for test/PoseidonHasherAudit.t.sol:PoseidonHasherTest
[PASS] test_PoCHashMaxUint() (gas: 19607)
Traces:
[19607] PoseidonHasherTest::test_PoCHashMaxUint()
[11098] PoseidonHasher::hash(115792089237316195423570985008687907853269984665640564039457584007913 c
129639935 [1.157e77]) [staticcall],!
[Return] 3366645945435192953002076803303112651887535928162668198103357554665518664470
[3.366e75],!
[0] VM::assertNotEq(3366645945435192953002076803303112651887535928162668198103357554665518664470
[3.366e75], 11254588113248280256028662529799552354366536761492627237202955510067774853962
[1.125e76], "Hash mismatch for max uint256 (Overflow issue)") [staticcall]
,!
,!
← [Return]
← [Stop]
Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 456.63μs (161.25μs CPU time)

## Recommendation
Recommended Mitigation: One of the following approaches should be adopted (depending on intended protocol
design):
1. If the intended domain is Fr (recommended for RLN):
• Enforce privateKey < Q in the off-chain SDK and/or circuits.
• Document that PoseidonHasher expects field elements, not arbitrary uint256 values.
• This guarantees (input + C1) < 2ˆ256, eliminating wraparound altogether.
2. If arbitrary uint256 inputs must be supported: Add explicit field reduction before absorbing the input:
input := mulmod(input, 1, Q) // input = input mod Q
let s1 := add(input, C1)
This ensures on-chain hashing matches canonical Poseidon semantics.
