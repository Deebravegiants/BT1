# [H] LibClone: Length overﬂow allows corruption of created proxy

## Summary
Severity: High
Contest weight: 0.8456
Dataset id: 6043
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating an immutable proxy with args with either the clone(address, bytes memory) or cloneDeterministic(address, bytes memory, bytes32) functions it's assumed that the length of the bytes input +100 (0x62 + 2) will fit in 2-bytes.
Excerpt from clone(address, bytes) (both the non-create2 & create2 variants of this clone function have the same logic & flaw):
```solidity
let extraLength := add(dataLength, 2)
mstore(
    sub(data, 0x5a),
    or(shl(0x78, add(extraLength, 0x62)), 0x6100003d81600a3d39f336602c57343d527f)
)
```
The assumption that "The inserted data length will fit in 2-bytes" is not explicitly checked anywhere. A final length that is larger than 2-bytes is not truncated either, being first bit shifted to the left by 15-bytes (0x78 bits) and then bitwise OR-ed with the data for insertion. This means that a final length requiring 3 or more non-zero bytes (≥65536) would actually change the meaning of the final bytecode:
- OR(0x6100003d81, 0x0001230000) = 0x6101233d81 => `PUSH2 0x0123 RETURNDATASIZE DUP2 ...`
+ OR(0x6100003d81, 0x0200230000) = 0x6300233d81 => `PUSH4 0x00233d81 ...`
This allows you to modify the PUSH2 byte (0x61) into a different opcode while still resulting in runnable code.
Speciﬁcally the ﬁrst PUSH2 can be changed into any even PUSH<n> opcode (PUSH4, PUSH6, PUSH8, PUSH10, ...) depending on the length in the resulting inserted length. Extending the length of the initial push opcode means that subsequent opcodes will be turned from logical operations into part of the word that'll get pushed onto the stack as part of execution. If suﬃciently extended it'll consume the op-byte of other subsequent push opcodes, turning their "value bytes" into logical opcodes, e.g.:
- 6101023d8160ff => PUSH2 0x01 0x02 RETURNDATASIZE DUP2 PUSH1 0xff
+ 6401023d8160ff => PUSH5 0x01 0x02 0x3d 0x81 0x60 SELFDESTRUCT
In the clone{Deterministic} functions this can be used to achieve 1 of 2 things:
1. Cause a proxy deployment to fail that would otherwise be considered valid (predictDeterministicAddress would still compute an address for the undeployable contract).
2. Cause a valid, empty contract (no bytecode) to deployed
Action 2. might be especially harmful as a library consumer may assume that if the cloning does not revert it must've been successful. Any funds sent to such a contract would be permanently forever lost & inaccessible.

## Proof of Concept
```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;
import {Test} from "forge-std/Test.sol";
import {LibClone} from "solady/utils/LibClone.sol";
contract LibCloneLengthOverflowPoC is Test {
    function test_length_overflow_PoC() public {
        bytes memory d = new bytes(0xe0000);
        address proxy = LibClone.clone(makeAddr("implementation"), d);
        // Successfully created contract
        assertTrue(proxy != address(0));
        // Proxy is however corrupted, having no runtime code.
        assertEq(proxy.code, new bytes(0));
        // Corrupted proxy also silently accepts ETH which is then permanently stuck.
        hoax(makeAddr("sender"), 1 ether);
        (bool success,) = proxy.call{value: 1 ether, gas: 2100}("");
        assertTrue(success);
        assertEq(proxy.balance, 1 ether);
    }
}
```
While the length of the data (0xe0000 bytes = 0.91 Mb) required to deploy a corrupted proxy may seem atypical it is feasible to create a bytes memory value of that size in a contract under mainnet gas constraints costing min. ~1.7M gas in memory expansion and EIP-3860 initcode costs.

## Recommendation
It is recommended the length of data is checked in both clone(address implementation, bytes memory data) and cloneDeterministic(address implementation, bytes memory data, bytes32 salt) not to exceed 65,435 such that the final max runtime size (65,435 + 2 + 0x62 = 65535) never exceeds 2 bytes.
