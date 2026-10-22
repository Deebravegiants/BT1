# [M] Messi paymaster should approve to zero first

## Summary
Severity: Medium
Contest weight: 0.6779
Dataset id: 22808
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some tokens like USDT revert in case the prior approval is non zero.
The messi paymaster approves tokens twice to bridge, which will lead to a revert in case a user tries to bridge tokens like USDT
In addition to this the first approve does not include fees, and on its own is incorrect.
The messi paymaster approves tokens first in line 420:
```solidity
tokenToBridge.approve(markets[bridgeOp.exchangeID], bridgeOp.amountIn);
```
After this messi tries to approve tokens again in line 520:
```solidity
tokenToBridge.approve(markets[bridgeOp.exchangeID], bridgeOp.amountIn);
```
The second approve is made in case the fee token should be bridged, and fees are deducted.
As we can see we try to approve tokens twice without approving to zero first, which will lead to an revert.
Messi paymaster cant bridge tokens like USDT which revert on non zero approval.

## Proof of Concept
Add following code to MockERC20.sol:
```solidity
function approve(address spender, uint256 amount) public virtual override returns (bool) {
    if (allowance(msg.sender,spender) != 0) {
        require(amount == 0, "USDT reverts here");
    }
    super.approve(spender,amount);
}
```
(simulation of USDT)
Run messi tests again and see both bridge tests using tokens revert for reason: "USDT reverts here".

## Recommendation
Remove the first approve, it does not include fees so it is incorrect. A more secure way is to develop a helper lib contract, that just always approves to zero first before approve. This will avoid all future issues regarding this problem.
