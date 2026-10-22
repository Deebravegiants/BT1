# [H] Lack of access control in the

## Summary
Severity: High
Contest weight: 0.3750
Dataset id: 23205
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An attacker can set himself as an extension, which is an allowed protocol-wide operator. As such, he can act on an account's behalf in all its positions and, for example, withdraw its collateral.
A new authorization functionality was introduced in Perennial 2.3 update to allow for signers and extensions to act on behalf of the account. Unfortunately, the updateExtension() function within the MarketFactory is missing the onlyOwner access control modifier.
File: MarketFactory.sol
100: function updateExtension(address extension, bool newEnabled) external {
101:     extensions[extension] = newEnabled;
102:     emit ExtensionUpdated(extension, newEnabled);
103: }
This extensions mapping is later used in the authorization() function to determine if the sender is an account operator:
File: MarketFactory.sol
77: function authorization(
78:     address account,
79:     address sender,
80:     address signer,
81:     address orderReferrer,
82:     out uint256 orderReferralFee
83: )
84:     view
85:     returns (bool, bool, uint256)
86: {
87:     return (
88:         account == sender || extensions[sender] || operators[account][sender],
89:         account == signer || signers[account][signer],
90:         referralFees(orderReferrer)
91:     );
92: }
The authorization() function is used within the Market contract to authorize the order in the name of the account:
File: Market.sol
500: // load factory metadata
501: (updateContext.operator, updateContext.signer, updateContext.orderReferralFee) =
502:     IMarketFactory(address(factory())).authorization(context.account, msg.sender, signer, orderReferrer);
503: if (guaranteeReferrer != address(0)) updateContext.guaranteeReferralFee = guaranteeReferralFee;
File: InvariantLib.sol
78: if (
79:     !updateContext.signer && // sender is relaying the account's signed intention
80:     !updateContext.operator && // sender is operator approved for account
81:     context.amount != 0 // sender is depositing zero or more into account, without position change
82: ) revert IMarket.MarketOperatorNotAllowedError();
As can be seen, anyone without authorization can set himself as an extension and act as the operator of any account, leading to the loss of all funds.
• Loss of funds.
• Missing access control.

## Recommendation
Add the onlyOwner modifier to the MarketFactory.updateExtension() function.
