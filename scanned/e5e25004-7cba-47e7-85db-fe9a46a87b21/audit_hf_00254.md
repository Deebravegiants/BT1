# [M] `NFTXMarketplaceZap.sol#buyAnd***`

## Summary
Severity: Medium
Contest weight: 0.4371
Dataset id: 1299
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function buyAndSwap721WETH(
      uint256 vaultId, 
      uint256[] memory idsIn, 
      uint256[] memory specificIds, 
      uint256 maxWethIn, 
      address[] calldata path,
      address to
    ) public nonReentrant {
      require(to != address(0));
      require(idsIn.length != 0);
      IERC20Upgradeable(address(WETH)).transferFrom(msg.sender, address(this), maxWethIn);
      INFTXVault vault = INFTXVault(nftxFactory.vault(vaultId));
      uint256 redeemFees = (vault.targetSwapFee() * specificIds.length) + (
          vault.randomSwapFee() * (idsIn.length - specificIds.length)
      );
      uint256[] memory amounts = _buyVaultToken(address(vault), redeemFees, maxWethIn, path);
      _swap721(vaultId, idsIn, specificIds, to);

      emit Swap(idsIn.length, amounts[0], to);

      // Return extras.
      uint256 remaining = WETH.balanceOf(address(this));
      WETH.transfer(to, remaining);
    }
```

For example:

If Alice calls `buyAndSwap721WETH()` to buy some ERC721 and send to Bob, for slippage control, Alice put `1000 ETH` as `maxWethIn`, the actual cost should be lower.

Let’s say the actual cost is `900 ETH`.

Expected Results: Alice spend only for the amount of the actual cost (`900 ETH`).

Actual Results: Alice spent `1000 ETH`.

I think the idea in this is that if a contract is buying for someone else, the zap handles the refund instead of the contract originating the purchase. But this is a valid concern, thank you.

This does result in a loss of funds if the user sends the wrong amount. I agree with the warden’s severity rating.

## Recommendation
No recommendation
