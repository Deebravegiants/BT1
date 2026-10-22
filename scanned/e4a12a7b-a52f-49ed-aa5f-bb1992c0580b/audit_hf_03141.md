# [M] Aer.lock only locks itself.

## Summary
Severity: Medium
Contest weight: 0.3971
Dataset id: 17638
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Aer.lock doesn't lock other Aer's functionalities.  
Aer.lock sets live to 0, locks surplusAuction and debtAuction and clean the states.  
```solidity
function lock() external override checkCaller {
    if (live == 0) revert Aer__lock_notLive();
    live = 0;
    queuedDebt = 0;
    debtOnAuction = 0;
    surplusAuction.lock(codex.credit(address(surplusAuction)));
    debtAuction.lock();
    codex.settleUnbackedDebt(min(codex.credit(address(this)), codex.unbackedDebt(address(this))));
    emit Lock();
}
```  
However, Aer only checks live in Aer.lock. The rest functions work as usual. surplusAuction and debtOnAuction can be reset.  
Aer can still work after being locked. The only thing it cannot do after being locked is locking again.

## Recommendation
Add live checks into other functions that should not work when Aer is locked.  
This is expected behavior. During shutdown (Tenebrae) Aer is used to track the global settlement process. https://github.com/fiatdao/fiat/blob/main/src/Tenebrae.sol#L341.
