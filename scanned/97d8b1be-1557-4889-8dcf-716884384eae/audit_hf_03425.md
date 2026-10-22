# [M] withdrawAllAndUnwrap

## Summary
Severity: Medium
Contest weight: 0.6003
Dataset id: 18721
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the withdrawAllAndUnwrap function of the protocol’s owner‑only contract. When the caller sets the sendToOperator flag to true, the function transfers the entire clpToken balance held by the contract to the address stored in the operator variable, which is normally an AMO.sol contract. The AMO contract is designed to receive only newly minted clpToken that originates from the curvePool during specific operations such as rebalanceDown, addLiquidity or addLiquidityOnlyStETH. It does not contain any logic to withdraw or otherwise use clpToken that arrives from external transfers. Consequently, any clpToken sent to the AMO by withdrawAllAndUnwrap becomes permanently locked inside the AMO’s balance because there is no function that moves those tokens out or accounts for them. The root cause is a mismatch between the token handling expectations of the AMO (which assumes incoming tokens are always freshly minted from the curvePool) and the actual transfer performed by withdrawAllAndUnwrap, which can deliver arbitrary existing clpToken. An attacker who controls the owner role can trigger this behaviour by calling withdrawAllAndUnwrap with sendToOperator set to true, causing the protocol’s liquidity to be drained into an address that cannot release it. From a user’s perspective the symptom is that after a withdrawal the expected clpToken balance is missing; the UI may show a successful transaction but the user’s wallet receives zero tokens and the protocol’s total liquidity appears reduced. This issue was discovered during a manual audit that compared the token flow in AMO.sol with the transfer logic in withdrawAllAndUnwrap and identified that the AMO never processes tokens received from external contracts. The problem is subtle because the transfer itself does not revert and emits no error, making the loss of funds appear as a normal operation. To remediate the issue the withdrawAllAndUnwrap function should either transfer the clpToken directly to msg.sender (the caller) or, if sending to the operator is required, the AMO contract must be extended with a safe withdrawal or accounting mechanism that can handle arbitrary clpToken balances. In broader terms this is a token‑locking bug caused by an incomplete token‑handling contract interface, leading to funds disappearing from the protocol’s usable pool and breaking the accounting assumptions that all clpToken held by the AMO is controllable.

## Proof of Concept
`withdrawAllAndUnwrap()` allows specifying `sendToOperator==true` to transfer the `clpToken` to `operator`.

The code is as follows:

```solidity
function withdrawAllAndUnwrap(
    bool claim,
    bool sendToOperator
) external onlyOwner {
    IBaseRewardPool(cvxPoolInfo.rewards).withdrawAllAndUnwrap(claim);
    if (sendToOperator) {
        uint256 totalBalance = clpToken.balanceOf(address(this));
        clpToken.safeTransfer(operator, totalBalance); // @audit transfer to operator (AMO)
    }
}
```

Currently in the protocol, `operator` is set to `AMO.sol` as normal.

But `AMO.sol` doesn’t have any way to use the transferred `clpToken`. The reason is that in AMO.sol, the method that transfers the `clpToken`, the number of transfers is from the newly generated `clpToken` from `curvePool`.

It doesn’t include `clpToken` that already exists in `AMO.sol` contract, for example (rebalanceDown/addLiquidity/addLiquidityOnlyStETH).

Example `rebalanceDown`:

```solidity
function rebalanceDown(
    RebalanceDownQuote memory quote
)
...
    lpAmountOut = curvePool.add_liquidity(amounts, quote.minLpReceived);

    IERC20(address(curvePool)).safeTransfer(
        address(cvxStaker),
        lpAmountOut // @audit this clpToken from curvePool
    );
    cvxStaker.depositAndStake(lpAmountOut);
```

So the `clpToken` transferred to ‘AMO.sol’ by `withdrawAllAndUnwrap()` will stay in the AMO contract and it is locked.

## Recommendation
Modify `withdrawAllAndUnwrap()`, directly transfer to `msg.sender`.
