# [M] Subaccount can be console account

## Summary
Severity: Medium
Contest weight: 0.2262
Dataset id: 4032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Suppose someone sets up a pseudo subaccount safe by directly calling createProxyWithNonce(), with the same parameters that would be used to create a subAccount. Then he uses this pseudo subaccount safe to call registerWallet(). This will be possible because subAccountToWallet[] hasn't been filled for this pseudo subaccount safe. Next he removes the pseudo subaccount safe via selfdestruct.
After this he creates a subaccount via deploySubAccount(), which result in the same address. The result is that the subaccount is also a console account.
function registerSubAccount(address _wallet, address _subAccount) external {
if (msg.sender != AddressProviderService._getAuthorizedAddress(_SAFE_DEPLOYER_HASH)) revert InvalidSender();
if (subAccountToWallet[_subAccount] != address(0)) revert AlreadyRegistered();
subAccountToWallet[_subAccount] = _wallet;
walletToSubAccountList[_wallet].push(_subAccount);
emit RegisterSubAccount(_wallet, _subAccount);
}
This will make other functions work in an unexpected way. For example _validateMsgSenderConsoleAccount() will return true and allow a subaccount to do registerExecutor().
function _validateMsgSenderConsoleAccount(address _account) internal view {
// ...
// msg.sender is console account
if (msg.sender == _account && _walletRegistry.isWallet(msg.sender)) return;
// ...
}
Also updatePolicy() will allow the subaccount to update a policy.
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

## Recommendation
Consider checking the _subAccount isn't registered as a wallet in registerSubAccount().
function registerSubAccount(address _wallet, address _subAccount) external {
// ...
if (isWallet[_subAccount]) revert AlreadyRegistered();
// ...
}
