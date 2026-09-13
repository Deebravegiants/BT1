# [H] 6.2 L2 DAI Allows Stealing

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

The transfer function of the L2 DAI contract allows stealing tokens from other users. The attack works
as follows:

```
1.Within the amount field of the transfer function the user specifies an invalid Uint256. Note that
uint256_check is never called. To steal i token wei, the attacker specifies P-i to be
amount.low and 0 to be amount.high. The low amount could be interpreted as the negative
number -i.
2.The uint256_le(amount, sender_balance) check will be passed as it will ultimately
compute the following:
```
```
1 - is_nn(amount.low - (sender_balance.low+1))
```
```
If for example the sender's (attacker's balance) is 0, that check will pass.
3.The uint256_sub(sender_balance, amount) computation will result in an increased
sender_balance due to the specially crafted amount.
4.The uint256_add(recipient_balance, amount) computation will result in a decreased
recipient_balance due to the specially crafted amount.
```
Note that the decrease of the recipient_balance is also the increase of the sender_balance. In
other words, the sender gains as many tokens as the recipient loses. Or more concisely, the sender can
steal all of the tokens of the receiver. So, if i==1 then one token wei is stolen. If i==2 then two wei are
stolen.


The only precondition for the attack is that the uint256_le(amount, sender_balance) can be
passed for manipulated amount values. Note that the current hints prevent a proof generation for this
attack in uint256_add, but hints can freely be changed and the verifier will accept it.

Code corrected:

amount is now validated in the internal function _transfer. Thus, neither transfer() nor
transfer_from can perform computations with invalid integers. Ultimately, the Uint256 library
functions receive the expected inputs and, thus, perform the documented computations.
