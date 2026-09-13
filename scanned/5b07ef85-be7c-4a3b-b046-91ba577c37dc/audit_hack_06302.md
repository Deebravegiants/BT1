# [M] `liquidate()` function is vulnerable to sandwich attack

## Summary
Severity: Medium
Reporter: 0xSmartContract
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320-L352
Type: audit-issue

## Details
# `liquidate()` function is vulnerable to sandwich attack

## Summary

In `liquidate()` function, `IAlchemist(self.alchemist).liquidate` external call is made with the following code, but since `_min_amount_out` in this call is fixed number `1`, it is vulnerable to sandwich attack

```vyper
contracts/Vault.vy:
  364  
  365:     amount_shares_liquidated: uint256 = IAlchemist(self.alchemist).liquidate(
  366:         ALCX_YVWETH,                 # _yield_token: address,
  367:         shares_to_liquidate,         # _shares: uint256,
  368:         1                            # _min_amount_out: uint256 -> covered by _min_weth_out
  369:     )

```
## Vulnerability Detail

Function `liquidate()` is called in every liquidate in Vault contract.
Liquidates the underlying debt of position[_token_id] by burning a corresponding amount of shares. Withdraws remaining value of shares as WETH to token_owner. Reverts if owner would receive less than _min_weth_out.


However `amount_shares_liquidated:` always has the value 1 when called by `liquidate` function.


The `liquidate()`method has the  `_min_weth_out` parameter, which basically serves as the slippage tolerance parameter. The problem is that everywhere in the code where `amount_shares_liquidated` is called, the value of `_min_amount_out` is just 1 wei, which basically means all swaps executed in the compound method can be sandwiched and the user can lose a huge amount of value due to slippage.


## Impact
[Vault.vy#L320-L352](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320-L352)

## Code Snippet

```vyper
contracts/Vault.vy:
  341  
  342: @nonreentrant("lock")
  343: @external
  344: def liquidate(_token_id: uint256, _min_weth_out: uint256) -> uint256:
  345:     """
  346:     @notice
  347:         Liquidates the underlying debt of position[_token_id] by burning
  348:         a corresponding amount of shares.
  349:         Withdraws remaining value of shares as WETH to token_owner.
  350:         Reverts if owner would receive less than _min_weth_out.
  351:     """
  352:     token_owner: address = ERC721(NFT).ownerOf(_token_id)
  353:     assert token_owner == msg.sender, "only token owner can liquidate"
  354: 
  355:     position: Position = self.positions[_token_id]
  356:     assert position.is_liquidated == False, "position already liquidated"
  357:     
  358:     position.is_liquidated = True
  359:     self.positions[_token_id] = position
  360:     self.total_shares -= position.shares_owned
  361: 
  362:     collateralisation: uint256 = self._latest_collateralisation()
  363:     shares_to_liquidate: uint256 = position.shares_owned * DECIMALS / collateralisation
  364: 
  365:     amount_shares_liquidated: uint256 = IAlchemist(self.alchemist).liquidate(
  366:         ALCX_YVWETH,                 # _yield_token: address,
  367:         shares_to_liquidate,         # _shares: uint256,
  368:         1                            # _min_amount_out: uint256 -> covered by _min_weth_out
  369:     )
  370: 
  371:     amount_to_withdraw: uint256 = position.shares_owned - amount_shares_liquidated
  372:     # _withdraw_underlying_from_alchemix reverts on < _min_weth_out
  373:     amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(amount_to_withdraw, token_owner, _min_weth_out)
  374: 
  375:     log Liquidated(_token_id, token_owner, amount_withdrawn)
  376:     return amount_withdrawn
  377: 
  378: 
  379: @internal
  380: def _latest_collateralisation() -> uint256:
  381:     """
  382:     @notice
  383:         Calculates the current collateral to debt ratio on Alchemix.
  384:         Reverts when there is no debt and collateralisation would be
  385:         infinite.
  386:     """
  387:     # Alchemist._validate(): 
  388:     # uint256 collateralization = totalValue(owner) * FIXED_POINT_SCALAR / uint256(debt);
  389:     current_debt: int256 = IAlchemist(self.alchemist).accounts(self)[0]
  390:     assert current_debt > 0, "zero debt"
  391:     
  392:     total_value: uint256 = IAlchemist(self.alchemist).totalValue(self)
  393:     debt: uint256 = convert(current_debt, uint256)
  394:     return total_value * DECIMALS / debt
  395: 
  396: 
  397: @internal
  398: def _withdraw_underlying_from_alchemix(
  399:     _amount_shares: uint256, 
  400:     _receiver: address,
  401:     _min_weth_out: uint256
  402: ) -> uint256:
  403:     """
  404:     @notice
  405:         Withdraws _amount_shares to _receiver expecting at least _min_weth_out
  406:     """
  407:     amount_withdrawn: uint256 = IAlchemist(self.alchemist).withdrawUnderlying(
  408:         ALCX_YVWETH,    # _yield_token: address,
  409:         _amount_shares, # _shares: uint256,
  410:         _receiver,      # _recipient: address,
  411:         _min_weth_out   # _min_amount_out: uint256 
  412:     )
  413:     assert amount_withdrawn >= _min_weth_out, "insufficient weth out"
  414:     return amount_withdrawn
```

## Tool used

Manual Review

## Recommendation
Add a setter to dynamically configure slippage tolerance amounts on-chain, or always make sure all transactions go through a private/dark mempool
