# [M] `RemoteAddressValidator` can incorrectly convert addresses to lower case

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-axelar
Published: 2023-07-21
Source: https://github.com/code-423n4/2023-07-axelar-findings/issues/323
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-axelar/blob/2f9b234bb8222d5fbe934beafede56bfb4522641/contracts/its/remote-address-validator/RemoteAddressValidator.sol#L58


# Vulnerability details

## Impact
The `validateSender` and `addTrustedAddress` functions of `RemoteAddressValidator` can incorrectly handle the passed address arguments, which will result in false negatives. E.g. a valid sender address may be invalidated.
## Proof of Concept
The [RemoteAddressValidator._lowerCase](https://github.com/code-423n4/2023-07-axelar/blob/2f9b234bb8222d5fbe934beafede56bfb4522641/contracts/its/remote-address-validator/RemoteAddressValidator.sol#L54) function is used to convert an address to lower case. Since the protocol is expected to support different EVM and non-EVM chains, account addresses may have different format, thus the necessity to convert them to strings and to convert the strings to lower case when comparing them. However, the function only converts the hexadecimal letters, i.e. the characters in ranges A-F:
```solidity
if ((b >= 65) && (b <= 70)) bytes(s)[i] = bytes1(b + uint8(32));
```

Here, `65` corresponds to `A`, and `70` corresponds to `F`. But, since different EVM and non-EVM chains are supported, addresses can contain other characters. For example, [Cosmos uses bech32 addresses](https://docs.cosmos.network/main/spec/addresses/bech32) and [Evmos supports both hexadecimal and bech32 addresses](https://docs.evmos.org/protocol/concepts/accounts#address-formats-for-clients).

If not all alphabetical characters of an address are converted to lower case, then the address comparison in the [validateSender](https://github.com/code-423n4/2023-07-axelar/blob/2f9b234bb8222d5fbe934beafede56bfb4522641/contracts/its/remote-address-validator/RemoteAddressValidator.sol#L69) can fail and result in a false revert.

## Tools Used
Manual review
## Recommended Mitigation Steps
In the `_lowerCase` function, consider converting all alphabetical characters to lower case, e.g.:
```diff
diff --git a/contracts/its/remote-address-validator/RemoteAddressValidator.sol b/contracts/its/remote-address-validator/RemoteAddressValidator.sol
index bb101e5..e83431b 100644
--- a/contracts/its/remote-address-validator/RemoteAddressValidator.sol
+++ b/contracts/its/remote-address-validator/RemoteAddressValidator.sol
@@ -55,7 +55,7 @@ contract RemoteAddressValidator is IRemoteAddressValidator, Upgradable {
         uint256 length = bytes(s).length;
         for (uint256 i; i < length; i++) {
             uint8 b = uint8(bytes(s)[i]);
-            if ((b >= 65) && (b <= 70)) bytes(s)[i] = bytes1(b + uint8(32));
+            if ((b >= 65) && (b <= 90)) bytes(s)[i] = bytes1(b + uint8(32));
         }
         return s;
     }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-axelar-findings/issues/323_
