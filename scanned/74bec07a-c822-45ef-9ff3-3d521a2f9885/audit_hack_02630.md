# [M] Use `call` instead of `transfer` and `send`

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Tomo
# Use `call` instead of `transfer` and `send`

## 💥 Impact

The `transfer()` function only allows the recipient to use**2300 gas**.

If the recipient uses more than that, transfers will fail. In the future gas costs might change increasing the likelihood of that happening.

## 🕵️‍♂️ Vulnerability Detail

The use of the deprecated `transfer()` function for an address will inevitably make the transaction fail when:

1. The claimer smart contract does not implement a payable function.
2. The claimer smart contract does implement a payable fallback which uses more than 2300 gas unit.
3. The claimer smart contract implements a payable fallback function that needs less than 2300 gas units but is called through proxy, raising the call's gas usage above 2300.

Additionally, using higher than 2300 gas might be mandatory for some multisig wallets.

## 📝 Code Snippet

```solidity
function withdrawPayments(uint256 _amount) external {
				/* ... */
        feeController.transfer(_amount);
    }
```

## 🚜 Tools Used

Manual

## ✅ Recommendation

When you sending ETH, you should use `.call.value(...)("")` method instead of `.trasnfer()` because `call` method can set the gas limit by yourself.And `("")` in the `.call` means not specifying the gas limit to be used.

Keep in mind that `call()` introduces the risk of reentrancy-attack. For more depth, please read this.
[https://hackernoon.com/hack-solidity-reentrancy-attack](https://hackernoon.com/hack-solidity-reentrancy-attack)

Follow the [checks-effects-interactions](https://fravoll.github.io/solidity-patterns/checks_effects_interactions.html) pattern to prevent this attack.

## 👬 Similar Issue

[https://swcregistry.io/docs/SWC-134](https://swcregistry.io/docs/SWC-134)

[https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now](https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/)

https://github.com/code-423n4/2022-05-rubicon-findings/issues/82
