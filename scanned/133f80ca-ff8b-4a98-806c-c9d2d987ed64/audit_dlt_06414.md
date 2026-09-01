# [H] LMPStrategy.sol#getRebalanceVaueStats() - Assumes that LMPVault token decimals are 18, which leads to incorrect accounting

## Summary
Severity: High
Chain: Smart contract
Component: Tokemak
Published: 2024-02-26
Source: https://github.com/hats-finance/Tokemak-0x4a2d708ea6b0c04186ecb774cfad1e50fb5efc0b/issues/5
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xe2da70c2745ee851e320312ebf772eb9ab0b40ee8d8f676da5e27c281e478e2d
**Severity:** high

**Description:**
**Description**\
When a call to `getRebalanceVaueStats` is done we have the following.

```solidity
 function getRebalanceValueStats(IStrategy.RebalanceParams memory params)//ok
        internal//ok
        returns (RebalanceValueStats memory)//ok
    {
        uint8 tokenOutDecimals = IERC20Metadata(params.tokenOut).decimals()//ok;
        uint8 tokenInDecimals = IERC20Metadata(params.tokenIn).decimals();//ok
        address lmpVaultAddress = address(lmpVault);//ok

        // Prices are all in terms of the base asset, so when its a rebalance back to the vault
        // or out of the vault, We can just take things as 1:1

        // Get the price of one unit of the underlying lp token, the params.tokenOut/tokenIn
        // Prices are calculated using the spot of price of the constituent tokens
        // validated to be within a tolerance of the safe price of those tokens
        uint256 outPrice = params.destinationOut != lmpVaultAddress//ok
            ? IDestinationVault(params.destinationOut).getValidatedSpotPrice() // hardcoded to 1e18
            //@audit-info try with low and high value tokens
            : 10 ** tokenOutDecimals;//ok

        uint256 inPrice = params.destinationIn != lmpVaultAddress//ok
            ? IDestinationVault(params.destinationIn).getValidatedSpotPrice()
            : 10 ** tokenInDecimals;//ok

        // prices are 1e18 and we want values in 1e18, so divide by token decimals
        uint256 outEthValue = params.destinationOut != lmpVaultAddress//ok
            ? outPrice * params.amountOut / 10 ** tokenOutDecimals//ok
            : params.amountOut;//ok

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Tokemak-0x4a2d708ea6b0c04186ecb774cfad1e50fb5efc0b/issues/5_
