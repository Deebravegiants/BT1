### Title
Swap functions use `block.timestamp` as deadline, leading to invalid expiration protection - ([Project: AuditingProject/AllProjects] [File: autonolas/deployed-source/0x1262136cac6a__BuyBackBurnerBalancer_tokenomics._Buy-ba/contracts/utils/BuyBackBurnerBalancer.sol])

### Summary
The `_performSwap` functions in `BuyBackBurnerBalancer.sol` and `BuyBackBurnerUniswap.sol` use `block.timestamp` as the deadline for swaps. This means transactions can remain valid indefinitely in the mempool, potentially leading to user fund loss if token prices change significantly after the user's intended execution time.

### Finding Description
The `_performSwap` function in `BuyBackBurnerBalancer.sol`  and the `_performSwap` function in `BuyBackBurnerUniswap.sol`  both utilize `block.timestamp` for the `deadline` parameter in their respective swap calls. Specifically, `BuyBackBurnerBalancer.sol` passes `block.timestamp` to `IBalancer(balVault).swap` , and `BuyBackBurnerUniswap.sol` sets `params.deadline` to `block.timestamp` for `IRouterV3(swapRouter).exactInputSingle` . This practice effectively removes any expiration protection, as the transaction's deadline is always set to the current block's timestamp, making it perpetually valid from the perspective of the smart contract.

### Impact Explanation
Transactions with `block.timestamp` as a deadline can be held in the mempool indefinitely and executed at a later time, even if market conditions have changed unfavorably for the user. While slippage protection (`amountOutMin`) is present, significant price movements can still occur within the slippage tolerance, leading to a worse execution price than the user intended and potential loss of funds.

### Likelihood Explanation
The likelihood of this vulnerability being exploited is medium. While it requires a transaction to be delayed in the mempool and significant price volatility, the absence of a proper deadline makes such a scenario possible.

### Recommendation
Modify the `_performSwap` functions to allow users to specify a future `deadline` for their transactions, rather than using `block.timestamp`. This would enable users to set an acceptable time window for their swaps, mitigating the risk of unfavorable execution due to delayed transactions.

### Proof of Concept
The `_performSwap` function in `autonolas/deployed-source/0x1262136cac6a__BuyBackBurnerBalancer_tokenomics._Buy-ba/contracts/utils/BuyBackBurnerBalancer.sol`  calls `IBalancer(balVault).swap` with `block.timestamp` as the deadline:
```solidity
        olasAmount = IBalancer(balVault).swap(singleSwap, fundManagement, amountOutMin, block.timestamp);
``` 

Similarly, the `_performSwap` function in `autonolas/deployed-source/0xCF05126771A2__BuyBackBurnerUniswap_tokenomics._Buy-bac/contracts/utils/BuyBackBurnerUniswap.sol`  sets the `deadline` parameter to `block.timestamp` for `ISwapRouter(swapRouter).exactInputSingle`:
```solidity
            deadline: block.timestamp,
``` 

These implementations mean that a transaction can be submitted to the network, held in the mempool, and executed at any future block, as long as the `amountOutMinimum` condition is met, regardless of how much time has passed since the transaction was initially broadcast.

## Notes
The `issues.md` file contains a section discussing "Unused slippage params" / "No Slippage Protection" . While this section addresses slippage, it concludes that `TakerTraitsLib.validate` enforces thresholds correctly and that thresholds are opt-in for signed limit orders, which is standard. This is distinct from the current finding, which focuses on the absence of a proper transaction deadline rather than the enforcement of slippage itself. The `issues.md` also mentions `PancakeSwapHandler` having a caller-supplied `isEnabled` flag that can disable slippage protection , which is a related but separate issue concerning slippage control rather than transaction expiration.

View this search on DeepWiki: https://deepwiki.com/search/-analog-scan-prompt-external-r_3b8d3a58-7266-4b83-8c39-f41e0a6ff1bd
