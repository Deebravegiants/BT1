# [M] Proper totalReserve Accounting in calInterest() And withdrawReserve() Public

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 12845
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Rabbit protocol has been designed to provide efficient position management with timely accounting of current debt as well as the actual value. By design, there is a need to timely collect interest accrued from the debt. While examining the interest collection, we notice the state totalReserve is not properly accounted for. To elaborate, we show below the related functions calInterest() and withdrawReserve(). The first function is used to compute accrued interest from the current debt and the second function allows the authorized entity to withdraw the reserve funds represented as totalReserve. Note that the internal accounting does not consider totalReserve as part of totalVal (reflected in calInterest()), which indicates the withdrawn reserve in the second function should not be used to decrease totalVal. The current implementation does decrease totalVal with the withdrawn reserve affects adverse influence to the share calculation for supplying users.
```solidity
function calInterest(address token) public {
    TokenBank storage bank = banks[token];
    require(bank.isOpen, "token not exists");
    if (now > bank.lastInterestTime) {
        uint256 timePast = now.sub(bank.lastInterestTime);
        uint256 totalDebt = bank.totalDebt;
        uint256 totalBalance = totalToken(token);
        uint256 ratePerSec = config.getInterestRate(totalDebt, totalBalance);
        uint256 interest = ratePerSec.mul(timePast).mul(totalDebt).div(1e18);
        uint256 toReserve = interest.mul(config.getReserveBps()).div(GLO_VAL);
        bank.totalReserve = bank.totalReserve.add(toReserve);
        bank.totalDebt = bank.totalDebt.add(interest);
        bank.lastInterestTime = now;
    }
}

function withdrawReserve(address token, address to, uint256 value) external onlyGov nonReentrant {
    TokenBank storage bank = banks[token];
    require(bank.isOpen, "token not exists");
    uint balance = token == address(0) ? address(this).balance : SafeToken.myBalance(token);
    if (balance >= bank.totalVal.add(value)) {
        bank.totalReserve = bank.totalReserve.sub(value);
        bank.totalVal = bank.totalVal.sub(value);
    }
    if (token == address(0)) {
        SafeToken.safeTransferETH(to, value);
    } else {
        SafeToken.safeTransfer(token, to, value);
    }
}
```

## Recommendation
Revise the aforementioned routines to better maintain the accurate totalReserve state
