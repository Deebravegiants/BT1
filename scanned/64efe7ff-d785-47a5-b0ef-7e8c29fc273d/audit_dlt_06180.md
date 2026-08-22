# [H] Safe can be permanently bricked if a broken guard were set

## Summary
Severity: High
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-11
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/26
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0x4883a703a6b6715810472be32412197600cabfee3a0c1bd9d9acb697792f3cc4
**Severity:** high

**Description:**
## Impact
User funds can be permanently frozen in `Safe`.`Safe` is only accessible from `modules` set before `guard`. 

## Description
Owner of a `Safe` can setup a guard contract that executes functions before every `Safe` transaction

`vendor/solidity/safe-contracts-1.4.1/contracts/Safe.sol` - [`execTransaction()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/vendor/solidity/safe-contracts-1.4.1/contracts/Safe.sol#L174-L177)
```solidity
        address guard = getGuard();
        {
            if (guard != address(0)) {
                Guard(guard).checkTransaction(
                // Transaction info
```
and after every `Safe` transactions
```solidity
		if (guard != address(0)) {
		    Guard(guard).checkAfterExecution(txHash, success);
		}
```
If the guard `check` functions revert for any reason, all of the `Safe` calls that are not executed from modules will revert. Since the guard setup is protected by `authorized` it can only be called by a `Safe` transaction, so it will revert as well. 

The `Safe` setup has been initialized with a `threshold` of one, so a single signer can:
1. accidentally set up a `guard` that will revert
2. intentionally set up a `guard` or be compromised to set up a `guard` that will revert

### Accidental setup
The good news is that in case the broken `guard` were set accidentally: the base module `HoprNodeManagementModule` is set up at initialization of the `Safe` and is still allowed to operate via `execTransactionFromModule()` and can also be upgraded to safe the user funds from the bricked `Safe`.

### Malicious signer
However in case one of the signers turn malicious: he can disable all `modules` like the `HoprNodeManagementModule`. This will make sure funds are permanently frozen after he sets up a reverting `guard`. Since private key compromises are in scope: and a single signer can execute this (because the `threshold` is set to one) I consider this a high severity vulnerability.

## Proof of Concept

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/26_
