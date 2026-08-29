# [M] The total deposit amount limit in `AccountingManager.sol` can be bypassed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1288
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L211


# Vulnerability details

## Impact
Vaults can be exposed to more risk than intended.  
## Proof of Concept  
Users can deposit funds in a vault through the vault's `AccountingManager.deposit()`. The `deposit()` function attempts to check if the TVL, with the new deposit accounted for, will be less than `depositLimitTotalAmount`. However, the `TVL()` function excludes the pending deposit amount `totalAWFDeposit` , which is incorrect since we might have any amount of pending deposits that, when summed together with the rest of the TVL, can exceed `depositLimitTotalAmount`.  
```solidity  
function deposit(address receiver, uint256 amount, address referrer) public nonReentrant whenNotPaused {  
    ...  
    if (amount > depositLimitPerTransaction) {  
        revert NoyaAccounting_DepositLimitPerTransactionExceeded();  
    }  
    // @audit -> TVL() doesn't account totalAWFDeposit  
    if (TVL() > depositLimitTotalAmount) {  
        revert NoyaAccounting_TotalDepositLimitExceeded();  
    }

    ...  
    depositQueue.totalAWFDeposit += amount;  
    }  
```  
```solidity  
function TVL() public view returns (uint256) {  
    return TVLHelper.getTVL(vaultId, registry, address(baseToken))  
    + baseToken.balanceOf(address(this))  
    - depositQueue.totalAWFDeposit;  
}  
```

## Tools used 
Manual Review  
## Recommended Mitigation Steps
The following mitigation can also be done by introducing another "TVL" function that doesn't exclude the pending deposit amount `totalAWFDeposit`.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1288_
