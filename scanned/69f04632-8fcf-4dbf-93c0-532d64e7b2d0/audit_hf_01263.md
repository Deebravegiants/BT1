# [M] BkdLocker depositFees can be blocked

## Summary
Severity: Medium
Contest weight: 0.5786
Dataset id: 5838
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the fee‑deposit mechanism of the BKDLocker contract, specifically the function that burns collected fees via a feeBurner helper. The logic assumes that when the contract sends native ETH to the feeBurner, at least one of the liquidity pools it iterates over is denominated in ETH (identified by an underlying address of 0). During the burn operation the feeBurner sets a flag, burningEth_, to true only if it encounters an ETH‑denominated pool. After the loop it validates the call with the condition require(burningEth_ || msg.value == 0, Error.INVALID_VALUE). If the contract holds a non‑zero ETH balance (msg.value > 0) but none of the pools have ETH as their underlying asset, burningEth_ remains false and the require statement fails, causing the whole burnFees transaction to revert. This situation can be triggered deliberately: an attacker sends a small amount of ETH to the BKDLocker contract (or exploits an existing balance) while all registered pools contain only ERC20 tokens. Subsequent fee‑deposit attempts invoke burnFees, which now tries to forward the existing ETH balance to feeBurner, but the lack of an ETH pool makes burningEth_ false, leading to a revert. The impact is a denial‑of‑service on the fee‑collection path – fees are never deposited into BKDLocker, revenue is stalled, and users may see missing refunds or zero balances where they expect fee payouts. The issue is subtle because the contract works correctly when at least one pool is ETH‑denominated; the failure only appears when an unexpected ETH balance coexists with an all‑ERC20 pool set, a condition that may not be obvious during routine testing. The root cause is a logical flaw in the handling of native ETH: the code unconditionally forwards the contract's ETH balance without confirming that an appropriate ETH pool is present, and the safety check mixes the presence of ETH with the existence of an ETH pool. To remediate, the contract should first detect whether any pool underlying token is native ETH (using an ethFound flag) and only forward ETH to feeBurner when such a pool exists. If no ETH pool is found, the call should be made without attaching ETH, or the contract should reject receiving ETH in the first place. Adding a pool that uses native ETH as its underlying asset also resolves the issue, as the burningEth_ flag would then become true and the require condition would pass. This fix restores the intended business logic that fees are always burned or forwarded correctly, preventing attackers from griefing the protocol by merely depositing a small amount of ETH.

## Proof of Concept
1. Assume RewardHandler.sol has currently amount 5 as address(this).balance (ethBalance) (even attacker can send a small balance to this contract to do this dos attack)
  2. None of the pools have underlying as address(0) so no ETH tokens and only ERC20 tokens are present
  3. Now feeBurner.burnToTarget is called passing current ETH balance of amount 5 with all pool tokens
  4. feeBurner loops through all tokens and swap them to WETH. Since none of the token is ETH so burningEth_ variable is false
  5. Now the below require condition fails since burningEth_ is false

```solidity
require(burningEth_ || msg.value == 0, Error.INVALID_VALUE);
```

  6. This fails the burnFees function.

## Recommendation
ETH should not be sent if none of pool underlying token is ETH. Change it to something like below:

```solidity
bool ethFound=false;
for (uint256 i; i < pools.length; i = i.uncheckedInc()) {
    ILiquidityPool pool = ILiquidityPool(pools[i]);
    address underlying = pool.getUnderlying();
    if (underlying != address(0)) {
        _approve(underlying, address(feeBurner));
    } else {
        ethFound=true;
    }
    tokens[i] = underlying;
}

if(ethFound){
    feeBurner.burnToTarget{value: ethBalance}(tokens, targetLpToken);
} else {
    feeBurner.burnToTarget(tokens, targetLpToken);
}
```

The warden has shown how, due to a flaw in the logic, if ETH is present in the contract and no pool is denominated in ETH, then the contract will revert.

This can be done as a DOS attack or for griefing.

However, remediation would simply require adding a pool denominated in ETH, to ensure that the logic goes through

For this reason, I believe Medium Severity to be more appropriate
