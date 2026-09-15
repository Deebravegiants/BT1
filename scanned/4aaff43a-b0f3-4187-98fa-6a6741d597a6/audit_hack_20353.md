# [M] 5.1.5 Subaccount can be console account

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** WalletRegistry.sol#L49-L55, ExecutorRegistry.sol#L77-L87, PolicyRegistry.sol#L35-L

**Description:** Suppose someone sets up apseudo subaccount safeby directly callingcreateProxyWithNonce(),
with the same parameters that would be used to create a subAccount. Then he uses thispseudo subaccount safe
to callregisterWallet(). This will be possible becausesubAccountToWallet[]hasn't been filled for thispseudo
subaccount safe. Next he removes thepseudo subaccount safeviaselfdestruct.

After this he creates a subaccount viadeploySubAccount(), which result in the same address. The result is that
the subaccount is also a console account.

```
function registerSubAccount(address _wallet, address _subAccount) external {
if (msg.sender != AddressProviderService._getAuthorizedAddress(_SAFE_DEPLOYER_HASH)) revert
,! InvalidSender();
if (subAccountToWallet[_subAccount] != address(0)) revert AlreadyRegistered();
subAccountToWallet[_subAccount] = _wallet;
walletToSubAccountList[_wallet].push(_subAccount);
emit RegisterSubAccount(_wallet, _subAccount);
}
```
This will make other functions work in an unexected way. For example_validateMsgSenderConsoleAccount()
will returntrueand allow a subaccount to doregisterExecutor().

```
function _validateMsgSenderConsoleAccount(address _account) internal view {
// ...
// msg.sender is console account
if (msg.sender == _account && _walletRegistry.isWallet(msg.sender)) return;
// ...
}
```
AlsoupdatePolicy()will allow the subaccount to update a policy.

```
function updatePolicy(address account, bytes32 policyCommit) external {
// ...
} else if (msg.sender == account && walletRegistry.isWallet(account)) {
// In case invoker is a registered wallet
} else {
revert UnauthorizedPolicyUpdate();
}
// solhint-enable no-empty-blocks
_updatePolicy(account, policyCommit, currentCommit);
}
```
**Recommendation:** Consider checking the_subAccountisn't registered as a wallet inregisterSubAccount().

```
function registerSubAccount(address _wallet, address _subAccount) external {
// ...
+ if (isWallet[_subAccount]) revert AlreadyRegistered();
// ...
}
```
**Brahma:** Solved in PR 56.

**Spearbit:** Verified.
