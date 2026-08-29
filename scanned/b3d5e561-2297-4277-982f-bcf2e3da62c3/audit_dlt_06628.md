# [H] `personalMint()` reentrancy attack

## Summary
Severity: High
Chain: Smart contract
Component: Circles
Published: 2024-09-05
Source: https://github.com/hats-finance/Circles-0x6ca9ca24d78af44582951825bef9eadcb210e5cf/issues/8
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xec7bc17cdbb6208d02f4a0ac0ea20b9ec3edd1f02deacab6e2ed24110ac2450f
**Severity:** high

**Description:**
## Impact
Attacker can claim the initial issuance as many times as he wants (only block.gaslimit limits how many times the reentrancy can be executed)

## Description
The `personalMint()` function allows a registered user to mint personal Circles for themselves: after registration and v1 status check it calls the `_claimIssuance()` function which soon calls `_mintAndUpdateTotalSupply()` -> `_mint()`  which mints and calls `.onERC1155Received` if the user is not an EOA aka passes the greater than zero `to.code.length` check in `_doSafeTransferAcceptanceCheck()`.


`Hub.sol` - `_claimIssuance()`
```solidity
    function _claimIssuance(address _human) internal {
        (uint256 issuance, uint256 startPeriod, uint256 endPeriod) = _calculateIssuance(_human);
        if (issuance == 0) {
            // No issuance to claim, simply return without reverting
            return;
        }
        // mint personal Circles to the human
        _mintAndUpdateTotalSupply(_human, toTokenId(_human), issuance, "");
        // update the last mint time
        mintTimes[_human].lastMintTime = uint96(block.timestamp);

        emit PersonalMint(_human, issuance, startPeriod, endPeriod);
    }
```

The user can reenter the `personalMint()` function from `.onERC1155Received()` and claim & mint issuance again and again an arbitrary amount of times because nor `registerHuman()` nor `personalMint()` prevents a contract calling these functions 

This wouldn't even be a huge problem if the `issuance` during the reentrancy would use the updated values for calculations in `_calculateIssuance()`: however `mintTimes[_human].lastTime` is only updated after the mint as we can see in `_claimIssuance()` which ultimately allows the attacker to claim their initial issuance as many times they want with continually reentering `personalMint()` from `.onERC1155Received()`.

### Full Execution flow
`personalMint()` -> `_claimIssuance()` -> `mintAndUpdateTotalSupply()` -> `_mint()` -> `_updateWithAcceptanceCheck()` -> `_acceptanceCheck()` -> `_doSafeTransferAcceptanceCheck()` -> `(to).onERC1155Received()`

## Proof of Concept

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Circles-0x6ca9ca24d78af44582951825bef9eadcb210e5cf/issues/8_
