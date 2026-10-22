# [M] Precision is lost in depositAuction and with-

## Summary
Severity: Medium
Contest weight: 0.7003
Dataset id: 17821
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Formulas for usdcAmount, portion.crab, portion.eth used in depositAuction() and withdrawAuction() for queued distributions perform division first, which lead to truncation and fund loss in the numerical corner cases. depositAuction() and withdrawAuction() use the same approach for USDC and crab amount calculation. Let's focus on withdrawAuction(), there it is usdcAmount=(((withdraw.amount*1e18)/_p.crabToWithdraw)*usdcReceived)/1e18. When _p.crabToWithdraw is big compared to withdraw.amount, the ((withdraw.amount*1e18)/_p.crabToWithdraw) can become zero as result of integer division. As an example there can be an ordinary user and a whale situation, for the user it can be withdraw.amount=900, while _p.crabToWithdraw=1000e18, usdcReceived=2e18, then usdcAmount=(((withdraw.amount*1e18)/_p.crabToWithdraw)*usdcReceived)/1e18=0, while it should be usdcAmount=(withdraw.amount*usdcReceived)/_p.crabToWithdraw=(900*2e18)/1000e18=1. When truncation occurs the corresponding depositor or withdrawer will experience the loss as less funds to be distributed to them. Setting the severity to medium as this have material impact in a numerical corner cases only.

withdrawAuction() use usdcAmount=(((withdraw.amount*1e18)/_p.crabToWithdraw)*usdcReceived)/1e18:
Netting.sol#L697-L718
```solidity
if (withdraw.amount <= remainingWithdraws) {
    // full usage
    remainingWithdraws -= withdraw.amount;
    crabBalance[withdraw.sender] -= withdraw.amount;
    // send proportional usdc
    usdcAmount = (((withdraw.amount * 1e18) / _p.crabToWithdraw) * usdcReceived) / 1e18;
    IERC20(usdc).transfer(withdraw.sender, usdcAmount);
    emit CrabWithdrawn(withdraw.sender, withdraw.amount, usdcAmount, j);
    delete withdraws[j];
    j++;
} else {
    withdraws[j].amount -= remainingWithdraws;
    crabBalance[withdraw.sender] -= remainingWithdraws;
    // send proportional usdc
    usdcAmount = (((remainingWithdraws * 1e18) / _p.crabToWithdraw) * usdcReceived) / 1e18;
    IERC20(usdc).transfer(withdraw.sender, usdcAmount);
    emit CrabWithdrawn(withdraw.sender, remainingWithdraws, usdcAmount, j);
    remainingWithdraws = 0;
}
```
depositAuction() use the same approach for portion.crab and portion.eth:
Netting.sol#L584-L618
```solidity
if (queuedAmount <= remainingDeposits) {
    remainingDeposits = remainingDeposits - queuedAmount;
    usdBalance[deposits[k].sender] -= queuedAmount;
    portion.crab = (((queuedAmount * 1e18) / _p.depositsQueued) * to_send.crab) / 1e18;
    IERC20(crab).transfer(deposits[k].sender, portion.crab);
    portion.eth = (((queuedAmount * 1e18) / _p.depositsQueued) * to_send.eth) / 1e18;
    if (portion.eth > 1e12) {
        IWETH(weth).transfer(deposits[k].sender, portion.eth);
    } else {
        portion.eth = 0;
    }
    emit USDCDeposited(deposits[k].sender, queuedAmount, portion.crab, k, portion.eth);
    delete deposits[k];
    k++;
} else {
    usdBalance[deposits[k].sender] -= remainingDeposits;
    portion.crab = (((remainingDeposits * 1e18) / _p.depositsQueued) * to_send.crab) / 1e18;
    IERC20(crab).transfer(deposits[k].sender, portion.crab);
    portion.eth = (((remainingDeposits * 1e18) / _p.depositsQueued) * to_send.eth) / 1e18;
    if (portion.eth > 1e12) {
        IWETH(weth).transfer(deposits[k].sender, portion.eth);
    } else {
        portion.eth = 0;
    }
    emit USDCDeposited(deposits[k].sender, remainingDeposits, portion.crab, k, portion.eth);
    deposits[k].amount -= remainingDeposits;
    remainingDeposits = 0;
}
```

## Recommendation
Consider performing multiplication first in all the case, for example for withdrawAuction():
Netting.sol#L697-L718
```solidity
if (withdraw.amount <= remainingWithdraws) {
    // full usage
    remainingWithdraws -= withdraw.amount;
    crabBalance[withdraw.sender] -= withdraw.amount;
    // send proportional usdc
    usdcAmount = (withdraw.amount * usdcReceived) / _p.crabToWithdraw;
    IERC20(usdc).transfer(withdraw.sender, usdcAmount);
    emit CrabWithdrawn(withdraw.sender, withdraw.amount, usdcAmount, j);
    delete withdraws[j];
    j++;
} else {
    withdraws[j].amount -= remainingWithdraws;
    crabBalance[withdraw.sender] -= remainingWithdraws;
    // send proportional usdc
    usdcAmount = (remainingWithdraws * usdcReceived) / _p.crabToWithdraw;
    IERC20(usdc).transfer(withdraw.sender, usdcAmount);
    emit CrabWithdrawn(withdraw.sender, remainingWithdraws, usdcAmount, j);
    remainingWithdraws = 0;
}
```
withdraw.amount and _p.crabToWithdraw have 18 decimals here, usdcReceived and resulting usdcAmount have 6 decimals.
