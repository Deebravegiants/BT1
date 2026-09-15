# [M] Malicious governance can use `updateWethTranferGas` to steal WETH from buyers

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-infinity
Published: 2022-06-18
Source: https://github.com/code-423n4/2022-06-infinity-findings/issues/127
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-infinity/blob/765376fa238bbccd8b1e2e12897c91098c7e5ac6/contracts/core/InfinityExchange.sol#L1260-L1263
https://github.com/code-423n4/2022-06-infinity/blob/765376fa238bbccd8b1e2e12897c91098c7e5ac6/contracts/core/InfinityExchange.sol#L739-L747


# Vulnerability details

A malicious or compromised governance can set the transfer gas cost to an unreasonable amount and steal approved WETH from buyers.

There are two ways for governance to exploit this:
- When an order is being executed, governance can frontrun the transactions by setting `WETH_TRANSFER_GAS_UNITS` to a very high amount. 
- Set `WETH_TRANSFER_GAS_UNITS` to a very high amount, and execute trades against active buy orders. As long as the value of WETH to steal is higher than the cost to prepare the NFTs to sell, it is profitable to do so.

#### Proof of Concept
- `WETH_TRANSFER_GAS_UNITS` is set to `50000`.
- Alice has 100 WETH and 100 USDC. She approved infinite allowance to `InfinityExchange`.
- Alice signs a buy order to buy a FakePunk NFT with 100 USDC price.
- Malicious governance sets `WETH_TRANSFER_GAS_UNITS` to a very high amount such that the [gasCost](https://github.com/code-423n4/2022-06-infinity/blob/765376fa238bbccd8b1e2e12897c91098c7e5ac6/contracts/core/InfinityExchange.sol#L739) calculation equals 100 WETH. 
- Governance then bought a FakePunk in open market, and fills Alice's order.
- Alice received the NFT but paid 100 WETH as gas cost.

#### Recommended Mitigation Steps
Set a sanity check in `updateWethTranferGas` so governance can't set it to unreasonable value. Consider using timelock for setting governance settings.
```
function updateWethTranferGas(uint32 _wethTransferGasUnits) external onlyOwner {
    require(_wethTransferGasUnits <= 100000, "gas unit must not be higher than 100000");
    WETH_TRANSFER_GAS_UNITS = _wethTransferGasUnits;
    emit NewWethTransferGasUnits(_wethTransferGasUnits);
}
```
