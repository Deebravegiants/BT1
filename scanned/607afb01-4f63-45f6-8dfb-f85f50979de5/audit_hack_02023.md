# [M] 6.4 DoS of LeverageActions

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 4 Code Corrected

LeveragedActions can be blocked completely or for specific collaterals only in different ways:

```
1.When opening an account the credit manager will check if onBehalfOf already has an
account. In case a malicious user has already transferred the ownership of a credit account to
the LeverageActions contract then the CreditManager will fail to open a new one:
```
```
function openCreditAccount(
...
require(
!hasOpenedCreditAccount(onBehalfOf) && onBehalfOf != address(0),
Errors.CM_ZERO_ADDRESS_OR_USER_HAVE_ALREADY_OPEN_CREDIT_ACCOUNT
); // T:[CM-3]
...
```
```
2.Although this is more a theoretical attack, assume a credit manager which prohibits the user to
invest more that A amount of tokens. A malicious user sends to the the contract A + 1 tokens.
When the contract will try to open a leveraged position it will do so using the total balance of the
token it holds. If this amount is greater than the allowed one the account opening will block.
The snippets which dictate the above behavior are the following:
```
```
LeverageActions:
```
```
function _openLong(LongParameters calldata longParams, uint256 referralCode){
```

```
...
uint256 amount = IERC20(collateral).balanceOf(address(this)); // M:[LA-1]
...
}
```
```
CreditManager:
```
```
function openCreditAccount(
...
require(
amount >= minAmount &&
amount <= maxAmount &&
leverageFactor > 0 &&
leverageFactor <= maxLeverageFactor,
Errors.CM_INCORRECT_PARAMS
); // T:[CM-2]
...
}
```
Code corrected:

For the case #1, an allowance system was implemented for the transfer of credit account. In order to get
a credit account transferred, the receiver needs to pre-approve the sender of the credit account. Hence
one can no longer transfer a credit account to the LeveragedAction contract and the issue no longer
exists.

To mitigate case #2 the LeveragedActions contract now uses the actual balance difference.

*Moreover, Gearbox Protocol pointed out a third way to use the attack described above. Specifically, a
user can open an account on behalf of the LeverageAccount contract which would result in a
Denial-of-Service for the LeverageAction contract. The issue has been resolved by also restricting the
address on behalf of which the credit account is opened.
