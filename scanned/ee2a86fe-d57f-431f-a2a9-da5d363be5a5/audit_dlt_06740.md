# [M] Delegation should not be allowed to address(0)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-nouns-builder
Published: 2022-09-11
Source: https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/203
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-nouns-builder/blob/main/src/lib/token/ERC721Votes.sol#L179-L190


# Vulnerability details

## Impact
Assuming an existing bug in the `_delegate` function is fixed (see my previous issue submission titled "Delegating votes leaves the token owner with votes while giving the delegate additional votes"):
if a user delegates to address(0) that vote gets lost.

## Proof of Concept

Assuming the `_delegate` function gets patched by changing:
`address prevDelegate = delegation[_from];`
to
`address prevDelegate = delegates(_from);`

The steps to be taken:

1. User (U) gets one NFT (e.g by winning the auction)
	a. votes(U) = 1
2. U delegates to address(0) // prevDelegate is U, so votes(U)--
	a. votes(U) = 0, votes(address(0)) = 0
3. U delegates to address(0) // prevDelegate is U, so votes(U)--
	a. votes(U) = 2^192 - 1

Below is a forge test showing the issue:

```
// SPDX-License-Identifier: MIT
pragma solidity 0.8.15;

import { NounsBuilderTest } from "../utils/NounsBuilderTest.sol";
import { TokenTypesV1 } from "../../src/token/types/TokenTypesV1.sol";

contract TokenTest is NounsBuilderTest, TokenTypesV1 {
    address user1 = address(0x1001);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/203_
