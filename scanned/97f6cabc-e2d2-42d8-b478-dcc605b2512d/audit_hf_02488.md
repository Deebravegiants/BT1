# [H] Exposure Of Permissioned UserManager::setUserReferrer()

## Summary
Severity: High
Contest weight: 0.5717
Dataset id: 13319
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function setUserReferrer(address user_, address referrer_) external {
    require(user_ != referrer_, "UserManager::setUserReferrer: User cannot be referrer");
    if (_userReferrer[user_] == address(0)) {
        if (referrer_ == address(0)) {
            _userReferrer[user_] = NO_REFERRER_ADDRESS;
        } else {
            _userReferrer[user_] = referrer_;
        }
        emit UserReferrerAdded(user_, referrer_);
    }
}
```
However, we notice that this routine is currently permissionless, which means it can be invoked by anyone to set the referrer of the user. Also, the referrer can only be set once. A bad actor could monitor the open position transaction from memory pool and front run the transaction to set the user referrer to his own address. To fix this issue, the permissionless function needs to be changed to be permissioned such that only the intended pair contract is allowed to successfully invoke it.

## Recommendation
Add the onlyValidTradePair(msg.sender) modifier to the above setUserReferrer() function.
