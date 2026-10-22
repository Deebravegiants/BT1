# [M] Delegation should not be allowed to address

## Summary
Severity: Medium
Contest weight: 0.5301
Dataset id: 16798
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[ERC721Votes.sol#L179-L190](https://github.com/code-423n4/2022-09-nouns-builder/blob/main/src/lib/token/ERC721Votes.sol#L179-L190)  
Assuming an existing bug in the `_delegate` function is fixed (see my previous issue submission titled ”[Delegating votes leaves the token owner with votes while giving the delegate additional votes](https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/198)”):  
if a user delegates to address(0) that vote gets lost.

## Proof of Concept
Assuming the `_delegate` function gets patched by changing:  
`address prevDelegate = delegation[_from];`  
to  
`address prevDelegate = delegates(_from);`

The steps to be taken:

  1. User (U) gets one NFT (e.g by winning the auction) a. votes(U) = 1
  2. U delegates to address(0) // prevDelegate is U, so votes(U)— a. votes(U) = 0, votes(address(0)) = 0
  3. U delegates to address(0) // prevDelegate is U, so votes(U)— a. votes(U) = 2^192 - 1

Below is a forge test showing the issue:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.15;

import { NounsBuilderTest } from "../utils/NounsBuilderTest.sol";
import { TokenTypesV1 } from "../../src/token/types/TokenTypesV1.sol";

contract TokenTest is NounsBuilderTest, TokenTypesV1 {
    address user1 = address(0x1001);
    address delegate1 = address(0x2001);
    address delegate2 = address(0x2002);

    function setUp() public virtual override {
        super.setUp();

        vm.label(user1, "user1");
        vm.label(delegate1, "delegate1");
        deployMock();
    }

    function setMockFounderParams() internal virtual override {
        address[] memory wallets = new address[](1);
        uint256[] memory percents = new uint256[](1);
        uint256[] memory vestingEnds = new uint256[](1);

        wallets[0] = founder;
        percents[0] = 0;
        vestingEnds[0] = 4 weeks;

        setFounderParams(wallets, percents, vestingEnds);
    }

    function test_pown2() public {
        // user1 gets one token
        vm.startPrank(address(auction));
        token.mint();
        token.transferFrom(address(auction), user1, 0);
        vm.stopPrank();

        // user1 has 1 token & 1 vote
        assertEq(token.balanceOf(user1), 1);
        assertEq(token.getVotes(user1), 1);

        vm.prank(user1);
        token.delegate(address(0));
        assertEq(token.getVotes(user1), 0);

        vm.prank(user1);
        token.delegate(address(0));
        assertEq(token.getVotes(user1), type(uint192).max);
    }
}
```

## Recommendation
Either:

  1. Don’t allow delegation to address(0) by adding a check  
or  

  2. If someone tries to delegate to address(0), delegate to the NFT owner instead

The Warden has shown how, due to incorrect accounting, the delegation of voting power to the address(0) will permanently burn that voting power.

Because this is contingent on the owner performing the delegation, I believe Medium Severity to be more appropriate.
