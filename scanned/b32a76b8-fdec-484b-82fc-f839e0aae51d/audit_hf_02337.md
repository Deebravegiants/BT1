# [M] Revisited Logic in PayrollManager::executePayroll()

## Summary
Severity: Medium
Contest weight: 0.4251
Dataset id: 12697
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As a payroll protocol, Parcel Payroll is designed to utilize funds stored in Gnosis Safe multisig with the spending limit module enabled for secure and ﬂexible management of funds. While examining the built-in logic in handling the leftover native coins, we notice the current implementation needs to be improved. In the following, we show below the speciﬁc routine, i.e., executePayroll(). As the name indicates, this routine is used to execute a speciﬁc payroll. By design, this contract will revert if there is any tokens left after the payroll execution. However, it comes to our attention that when validating whether there is any ether left, the current implementation enforces the following statement, i.e., require(address(this).balance == initialBalances[i]) (line 235), which needs to be revised as require(address(this).balance > initialBalances[i]).
```solidity
// Check if the contract has any tokens left
for (uint256 i = 0; i < paymentTokens.length; i++) {
    if (paymentTokens[i] == address(0)) {
        // Revert if the contract has any ether left
        require(address(this).balance > initialBalances[i], "CS018");
    } else if (IERC20(paymentTokens[i]).balanceOf(address(this)) > initialBalances[i]) {
        // Revert if the contract has any tokens left
        revert("CS018");
    }
}
```

## Recommendation
Revise the above executePayroll() routine to properly check whether there is any asset left.
