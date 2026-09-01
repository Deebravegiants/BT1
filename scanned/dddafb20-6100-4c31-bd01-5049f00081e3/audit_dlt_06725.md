# [H] Destruction of the `SmartAccount` implementation

## Summary
Severity: High
Chain: Smart contract
Component: 2023-01-biconomy
Published: 2023-01-09
Source: https://github.com/code-423n4/2023-01-biconomy-findings/issues/496
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/SmartAccount.sol#L166
https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/SmartAccount.sol#L192
https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/SmartAccount.sol#L229
https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/base/Executor.sol#L23


# Vulnerability details

## Description

If the `SmartAccount` implementation contract is not initialized, it can be destroyed using the following attack scenario:

- Initialize the `SmartAccount` **implementation** contract using the `init` function.
- Execute a transaction that contains a single `delegatecall` to a contract that executes the `selfdestruct` opcode on any incoming call, such as:

```solidity=
contract Destructor {
    fallback() external {
        selfdestruct(payable(0));
    }
}
```

The destruction of the implementation contract would result in the freezing of all functionality of the wallets that point to such an implementation. It would also be impossible to change the implementation address, as the `Singleton` functionality and the entire contract would be destroyed, leaving only the functionality from the Proxy contract accessible.

---

In the deploy script there is the following logic:

```typescript
const SmartWallet = await ethers.getContractFactory("SmartAccount");
const baseImpl = await SmartWallet.deploy();
await baseImpl.deployed();
console.log("base wallet impl deployed at: ", baseImpl.address);
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-biconomy-findings/issues/496_
