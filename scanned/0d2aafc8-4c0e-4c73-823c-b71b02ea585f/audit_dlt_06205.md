# [H] Front-running deposit to change withdrawal credentials will result in `32 ETH` theft

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-11
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/48
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xff7675bdcb5c7defa3cd4c84b284ca0ac7420af7bad74a92558bd90119397a42
**Severity:** high

**Description:**
## Impact
Attacker will gain `32 ether` deposit from users 

## Description
An attacker can front-run a deposit for it's deposit data and directly deposit 1 ether to the deposit contract, but change the withdrawal credentials. Because the way deposit is implemented on the beacon chain, the withdrawal address remains the initial one upon second deposit, therefore it is permanently changed to the attacker's address who will gain `32 ether` from the honest depositor.

---

### EtherFi - Deposit

There is a two ways to register as a validator in `EtherFi` contracts:
1. A user can call `StakingManager` - `batchRegisterValidators()` to register themselves and deposit `32 ether` to the ETH2 deposit contract
2. A user can call `LiquidityPool` - `batchRegisterAsBnftHolder()` -> `StakingManager` - `batchRegisterValidators()` which will deposit `1 ether` to the ETH2 deposit contract to set the the validator data and wait for the admin to call `batchApproveRegistration()` to send the remaining `31 ether`.

The first method is 100% vulnerable to this attack and the attacker will get `32 ETH` for a `1 ETH` cost attack. For the second way the  `batchApproveRegistration()` comment mentions it's not supposed to be vulnerable to the attack:
> This gets called by the LP and only will only happen when the oracle has confirmed that the withdraw credentials for the validators are correct. This prevents a front-running attack.

However the attacker can still front-run `batchRegisterAsBnftHolder()` and get a 1 ETH deposit for each of the user's validators.

### Consensus Specs - Deposit Contract & Client Implementation

Let's break down how the deposit contract's `deposit()` function works to better understand this attack:

[`consensus-specs/solidity_deposit_contract/deposit_contract.sol`](https://github.com/ethereum/consensus-specs/blob/dev/solidity_deposit_contract/deposit_contract.sol#L101-L159)
```solidity
    function deposit(
        bytes calldata pubkey,
        bytes calldata withdrawal_credentials,
        bytes calldata signature,
        bytes32 deposit_data_root
    ) override external payable {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/48_
