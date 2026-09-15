# [M] `MagnetarV2#burst` double counts `msg.value` for `TOFT_WRAP` operation, making the transaction revert unless the user overpays

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1504
Type: code-finding

## Details
# Lines of code

 https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/MagnetarV2.sol#L214-L216
 https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/MagnetarV2.sol#L236-L238


# Vulnerability details

## Impact

A user who wishes to wrap the native token using `MagnetarV2` will have their call always revert, unless they send double the amount of ether that is wrapped, and the excess ether simply remains in the Magnetar contract. This makes the expected functionality effectively useless.

## Proof of Concept

The execution flow for calling `MagnetarV2#burst` with `_action.id == TOFT_WRAP` erroneously increments `valAccumulator` by `_action.value` twice: once before the large `if` statement that executes the call based on `_action.id`, and once inside the if block for `_action.id == TOFT_WRAP`. There is no need for lines 236-238 to exist.

```solidity
File: tapioca-periph-audit\contracts\Magnetar\MagnetarV2.sol

213: 
214:             unchecked { // @audit call value is cached
215:                 valAccumulator += _action.value;
216:             }

                // ...

232:             } else if (_action.id == TOFT_WRAP) {
233:                 WrapData memory data = abi.decode(_action.call[4:], (WrapData));
234:                 _checkSender(data.from);
235:                 if (_action.value > 0) {
236:                     unchecked {
237:                         valAccumulator += _action.value; // @audit call value is cached again
238:                     }
239:                     ITapiocaOFT(_action.target).wrapNative{
240:                         value: _action.value
241:                     }(data.to);
242:                 } else {
243:                     ITapiocaOFT(_action.target).wrap(
244:                         msg.sender,
245:                         data.to,
246:                         data.amount
247:                     );
248:                 }
```

This means that the check at the end of the function, `valAccumulator` will be greater than `msg.value` by the amount that was wrapped, and the call will always revert. Note that if the user makes the call such that `msg.value` is twice the amount of `_action.value` of the wrapping action then the call will succeed, however the user will have sacrificed funds to the Magnetar contract.

```solidity
File: tapioca-periph-audit\contracts\Magnetar\MagnetarV2.sol

714:         require(msg.value == valAccumulator, "MagnetarV2: value mismatch");

```

## Tools Used

Manual review

## Recommended Mitigation Steps

Remove the following lines:

```diff
File: tapioca-periph-audit\contracts\Magnetar\MagnetarV2.sol

            } else if (_action.id == TOFT_WRAP) {
                WrapData memory data = abi.decode(_action.call[4:], (WrapData));
                _checkSender(data.from);
                if (_action.value > 0) {
-                   unchecked {
-                       valAccumulator += _action.value;
-                   }
                    ITapiocaOFT(_action.target).wrapNative{
                        value: _action.value
                    }(data.to);
                } else {
                    ITapiocaOFT(_action.target).wrap(
                        msg.sender,
                        data.to,
                        data.amount
                    );
                }
```


## Assessed type

Other
