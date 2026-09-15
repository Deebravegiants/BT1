# [M] Vault deposit into `Alchemix` can suffer slippage depending on outstanding debt in `Yearn`

## Summary
Severity: Medium
Reporter: joestakey
Source: https://github.com/alchemix-finance/v2-foundry/blob/f4a60d6363ada8b9648ab57df42618a4647fb12d/src/AlchemistV2.sol#L601-L602
Type: audit-issue

## Details
# Vault deposit into `Alchemix` can suffer slippage depending on outstanding debt in `Yearn`

## Summary
Depending on the outstanding debt in `Yearn`, a WETH deposit into Alchemix when `register_deposit` is called upon settling an auction may suffer from slippage.
 
## Vulnerability Detail
Upon an auction settlement, the `Vault(self.vault).register_deposit(token_id, winning_amount)` call transfers the winning bid amount of `WETH` from the `AuctionHouse` to the `Vault`, then deposits the `WETH` into the Alchemix `ALCX_YVWETH` vault. 

```vyper
File: contracts/AuctionHouse.vy
210:     if winning_amount > 0:
211:         ERC20(WETH).approve(self.vault, winning_amount)
212:         Vault(self.vault).register_deposit(token_id, winning_amount)
```

```vyper
File: contracts/Vault.vy
216:     # transfer WETH to self
217:     ERC20(WETH).transferFrom(msg.sender, self, _amount)
218: 
219:     # deposit WETH to Alchemix
220:     shares_issued: uint256 = self._deposit_to_alchemist(_amount)
```

```vyper
File: contracts/Vault.vy
293:     shares_issued: uint256 = IAlchemist(self.alchemist).depositUnderlying(
294:         ALCX_YVWETH,     # yield_token
295:         _amount,         # amount
296:         self,            # recipient
297:         1                # min_amount_out - cannot be frontrun in a significant way
298:                          #                  so to reduce complexity we go with 1
299:     )
300:     return shares_issued
```

The call stack of `depositUnderlying()` in `Alchemist` is as follows: AlchemistV2.depositUnderlying  -> AlchemistV2._wrap() -> AlchemistAdapter.wrap() 

https://github.com/alchemix-finance/v2-foundry/blob/f4a60d6363ada8b9648ab57df42618a4647fb12d/src/AlchemistV2.sol#L601-L602
```solidity
        // Before depositing, the underlying tokens must be wrapped into yield tokens.
        uint256 amountYieldTokens = _wrap(yieldToken, amount, minimumAmountOut);
```

https://github.com/alchemix-finance/v2-foundry/blob/f4a60d6363ada8b9648ab57df42618a4647fb12d/src/AlchemistV2.sol#L1348-L1349
```solidity
        TokenUtils.safeTransferFrom(underlyingToken, msg.sender, address(this), amount);
        uint256 wrappedShares = adapter.wrap(amount, address(this));
```

https://github.com/alchemix-finance/v2-foundry/blob/f4a60d6363ada8b9648ab57df42618a4647fb12d/src/adapters/yearn/YearnTokenAdapter.sol#L35 
```solidity
        return IYearnVaultV2(token).deposit(amount, recipient);
```

The issue is that this function issues shares based on the total outstanding debt of the contract, meaning shares are issued against the total amount that the deposited capital can be given in service of the debt that Strategies assume. This mean that between strategies updates, there can be discrepancies, leading to slippage (see https://github.com/yearn/yearn-vaults/blob/7e0718b709d38769700bd458381e1b19ea8e67ca/contracts/Vault.vy#L878-L892) 

## Impact
A `WETH` deposit may not entitle the winner of the auction to a claim of the same value, they may lose in the process due to that initial slippage upon deposit.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L212
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L293-L299


## Tool used
Manual Review

## Recommendation
Use a higher slippage, perhaps allowing the `Vault` to compute the expected shares received before a call to `IAlchemist(self.alchemist).depositUnderlying()`
