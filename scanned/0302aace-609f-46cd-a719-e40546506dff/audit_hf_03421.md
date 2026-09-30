# [H] Marketplace may call `onERC721Received`

## Summary
Severity: High
Contest weight: 1.0000
Dataset id: 18665
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract supports a “push-based” NFT supply, where the price and rate are embedded in the data bytes. This way, the lender doesn’t need to additionally approve the NFT, but can just transfer it directly to the contract. However, since the contract also interacts with the marketplace to buy/sell NFT, it has to prevent the issue where the marketplace also sends data bytes, which might tie 1 NFT with 2 different liens and create divergence.
    
```solidity
function onERC721Received(
    address operator,
    address from,
    uint256 tokenId,
    bytes calldata data
) external returns (bytes4) {
    if (data.length == 64) {
        // @audit marketplace is router so the executor contract might not be whitelisted
        if (registeredMarketplaces[operator]) { 
            /// @dev transfer coming from registeredMarketplaces will go through buyNftFromMarket, where the NFT
            /// is matched with an existing lien (realize PnL) already. If procceds here, this NFT will be tied
            /// with two liens, which creates divergence.
            revert Errors.Unauthorized();
        }
        /// @dev MAX_PRICE and MAX_RATE should each be way below bytes32
        (uint256 price, uint256 rate) = abi.decode(data, (uint256, uint256));
        /// @dev the msg sender is the NFT collection (called by safeTransferFrom's _checkOnERC721Received check)
        _supplyNft(from, msg.sender, tokenId, price, rate);
    }
    return this.onERC721Received.selector;
}
```

The contract prevents it by using the `registeredMarketplaces[]` mapping, where it records the address of the marketplace. This check is explicitly commented in the codebase.

However, this is not enough. The protocol plans to integrate with Reservoir’s Router contract, so only the Router address is whitelisted in `registeredMarketplaces[]`. But the problem is, the address that transfers the NFT is not the Router, but the specific Executor contract, which is not whitelisted.

As a result, the marketplace might bypass this check and create a new lien in `onERC721Received()` during the `buyNftFromMarket()` flow, thus making 2 liens track the same NFT.

## Proof of Concept
Function `_execBuyNftFromMarket()` does a low-level call to the exchange.
    
```solidity
// execute raw order on registered marketplace
bool success;
if (useToken == 0) {
    // use ETH
    // solhint-disable-next-line avoid-low-level-calls
    (success, ) = marketplace.call{value: amount}(tradeData);
} else if (useToken == 1) {
    // use WETH
    weth.deposit{value: amount}();
    weth.approve(marketplace, amount);
    // solhint-disable-next-line avoid-low-level-calls
    (success, ) = marketplace.call(tradeData);
}
```

The contract calls to Reservoir’s router contract, which then calls to a specific module to execute the buy. 

```solidity
function _executeInternal(ExecutionInfo calldata executionInfo) internal {
  address module = executionInfo.module;

  // Ensure the target is a contract
  if (!module.isContract()) {
    revert UnsuccessfulExecution();
  }

  (bool success, ) = module.call{value: executionInfo.value}(executionInfo.data);
  if (!success) {
    revert UnsuccessfulExecution();
  }
}
```

## Recommendation
Consider adding a flag that indicates the contract is in the `buyNftFromMarket()` flow and use it as a check in `onERC721Received()`. For example:
    
```solidity
_marketBuyFlow = 1;
_execBuyNftFromMarket(lien.collection, tokenId, amount, useToken, marketplace, tradeData);
_marketBuyFlow = 0;
```

And in `onERC721Receive()`:
    
```solidity
if (data.length == 64) {
  if(_martketBuyFlow) {
    return this.onERC721Received.selector;
  }
}
```
