# [M] Executing DCA Orders can fall in a permanent DoS for fee-on-transfer tokens & tokens implementing the approval race condition

## Summary
Severity: Medium
Reporter: 0xStalin
Source: https://github.com/d-xo/weird-erc20/blob/main/src/TransferFee.sol#L26
Type: audit-issue

## Details
# Executing DCA Orders can fall in a permanent DoS for fee-on-transfer tokens & tokens implementing the approval race condition

## Summary
- Execute DCA Orders can permanently become unusable for fee-on-transfer tokens & tokens implementing the approval race condition 

## Vulnerability Detail
- For tokens like USDT that do not allow approving an amount `M > 0` when an existing amount `N > 0` is already approved will cause that from the second transfer onwards all the transactions will revert because of the approval race condition in the ERC20's contract. [More info here](https://github.com/d-xo/weird-erc20#approval-race-protections)
- For fee-on-transfer tokens, the fee is deducted from the receiver, which means, that when using the safeTransferFrom()/transferFrom() to receive tokens from users into a contract, the fees of the transfer will be deducted from the received amount of tokens in the contract. [See here an example](https://github.com/d-xo/weird-erc20/blob/main/src/TransferFee.sol#L26)

- Now, the issue present in the `Dca::execute_dca_order()` is that on each call [the `UNISWAP_ROUTER` is approved using the exact amount of tokens that was requested to be transferred from the user into the contract](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204), the problem is caused because the requested amount is not the same amount that is received (because of the transfer's fees), thus, any unspent amount will make that the allowance is > 0, and in next executions, the approval race condition will make the tx to revert.
- The other issue caused by the fee-on-transfer is that [the swap is made using the requested amount of tokens](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L219), not the exactly received amount, so, if the contract has 0 tokens (it hasn't accrued fees or fees have been collected), the tx will be reverted because there are not enough funds in the contract, now, if the contract has some balance because of the protocol's fees, a portion of those fees will be used to complete the amount that will be used for the swap.

- In addition to the previous explanation, this contract is interacting directly with the UniswapV3 Router, and, as per [Uniswap Documentation](https://docs.uniswap.org/concepts/protocol/integration-issues), "Fee-on-transfer tokens will not function with our router contracts. As a workaround, the token creators may create a token wrapper or a customized router. We will not be making a router that supports fee-on-transfer tokens in the future."

## Impact
- Executing DCA Orders can permanently become unusable for fee-on-transfer tokens & tokens implementing the approval race condition 

## Code Snippet
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L200-L221

## Tool used
Manual Review & [weird-erc20-list](https://github.com/d-xo/weird-erc20)

## Recommendation
- So, in case the protocol would like to support fee-on-transfer tokens it will need to do the swaps directly in the UniV3Pools, without using the Uniswap Router.

-  If the protocol decides to support fee-on-transfer tokens, the mitigation for the described issues would be to:
  - 1. Compute the received amount of tokens in the contract after the safeTransferFrom()
  - 2. Make sure to always reset to 0 the approval before approving again

```solidity
def execute_dca_order(_uid: bytes32, _uni_hop_path: DynArray[address, 3], _uni_pool_fees: DynArray[uint24, 2], _share_profit: bool):
    ...
+   balance_before: uint256 = ERC20(order.token_in).balanceOf(address(this))

    # transfer token_in from user to self
    self._safe_transfer_from(order.token_in, order.account, self, order.amount_in_per_execution)

+   balance_after: uint256 = ERC20(order.token_in).balanceOf(address(this))

+   received_amount_from_user: uint256 = balance_after - balance_before

+  # approve UNISWAP_ROUTER to spend amount token_in
+   ERC20(order.token_in).approve(UNISWAP_ROUTER, order.amount_in_per_execution)

    ...

    uni_params: ExactInputParams = ExactInputParams({
        path: path,
        recipient: self,
        deadline: block.timestamp,
-       amountIn: order.amount_in_per_execution,
+       amountIn: received_amount_from_user,
        amountOutMinimum: min_amount_out
    })
    ...

   // do the swap directly on the pool, without using the Router. You can check the periphery contracts for a deeper explanation about how to achieve this.

```

- So, if the protocol decides to not support fee-on-transfer tokens, it might be necessary to either create a whitelist/blacklist (prevent usage of fee-on-transfer tokens at the on-chain level), or just document that the protocol won't support those types of tokens and add some validations on the app level (off-chain)
