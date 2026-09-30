# [M] Improved Handling of Corner Cases in _getPreviousBalance()

## Summary
Severity: Medium
Contest weight: 0.5930
Dataset id: 12392
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MasterVault smart contract allows users to stake their LND tokens into Legend vault to get rewards. As shown in the following code snippets, the Legends Never Die users can call the external function stake() to stake their LND tokens into a specified vault. When a user stakes his/her LND tokens into a specified _vid for the first time, the internal function _getPreviousBalance() (lines 242) is called to get the LND token total balance of all users from the previous vaults.
```solidity
function stake(uint256 _vid, uint256 _amount) external nonReentrant returns (uint256) {
    //get parameters
    VaultInfo storage vault = vaultInfo[_vid];
    UserInfo storage user = userInfo[_vid][_msgSender()];
    StakedInfo storage userStakedInfo = stakedInfoUser[_msgSender()];
    // checking , vault is started
    require(((vault.start <= block.number) && (vault.stop >= block.number)), "vault is not started or ended");
    // transfer Legends Never Die(FV) or Legends Never Die -BNB (LM) to contract
    baseToken.safeTransferFrom(_msgSender(), address(this), _amount);
    if (!vault.finalized) {
        vault.totalBalance = _getPreviousBalance(_vid);
        vault.totalBalanceStored = _getPreviousBalance(_vid);
        vault.finalized = true;
    }
}
```
We show below the current _getPreviousBalance() implementation. If there are no users staked their LND tokens into these previous vaults, the i-- operation is executed in the case of i = 0 (lines 385). Note that this does not result in an incorrect return value from _getPreviousBalance(), but does cause the function to revert unnecessarily when the above corner case occurs. Moreover, if there are no users staked their LND tokens into the first vault (vid = 0), the users will be unable to stake their LND tokens into the following vaults due to the revert.
```solidity
function _getPreviousBalance(uint256 _vid) internal view returns (uint256 balance) {
    if (_vid > 0) {
        for (uint256 i = _vid - 1; i >= 0; i--) {
            VaultInfo storage vault = vaultInfo[i];
            if (vault.totalBalance > 0) {
                balance = vault.totalBalance;
                break;
            }
        }
    }
}
```
Note a number of routines can be similarly improved, including MasterVault::_getPreviousBalanceStored(), and MasterVault::_exitAll().

## Recommendation
Revise the above decrement operation for i to avoid the unnecessary function revert.
