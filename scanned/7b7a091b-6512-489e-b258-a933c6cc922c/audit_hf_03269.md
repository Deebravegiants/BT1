# [H] Destruction of the `SmartAccount` implementation

## Summary
Severity: High
Contest weight: 0.6458
Dataset id: 17937
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[contracts/smart-contract-wallet/SmartAccount.sol#L166](https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/SmartAccount.sol#L166)  
[contracts/smart-contract-wallet/SmartAccount.sol#L192](https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/SmartAccount.sol#L192)  
[contracts/smart-contract-wallet/SmartAccount.sol#L229](https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/SmartAccount.sol#L229)  
[contracts/smart-contract-wallet/base/Executor.sol#L23](https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/base/Executor.sol#L23)

If the `SmartAccount` implementation contract is not initialized, it can be destroyed using the following attack scenario:

  * Initialize the `SmartAccount` **implementation** contract using the `init` function.
  * Execute a transaction that contains a single `delegatecall` to a contract that executes the `selfdestruct` opcode on any incoming call, such as:

    ```solidity
    contract Destructor {
        fallback() external {
            selfdestruct(payable(0));
        }
    }
    ```

The destruction of the implementation contract would result in the freezing of all functionality of the wallets that point to such an implementation. It would also be impossible to change the implementation address, as the `Singleton` functionality and the entire contract would be destroyed, leaving only the functionality from the Proxy contract accessible.

In the deploy script there is the following logic:
    
    const SmartWallet = await ethers.getContractFactory("SmartAccount");
    const baseImpl = await SmartWallet.deploy();
    await baseImpl.deployed();
    console.log("base wallet impl deployed at: ", baseImpl.address);

So, in the deploy script there is no enforce that the `SmartAccount` contract implementation was initialized.

The same situation in `scw-contracts/scripts/wallet-factory.deploy.ts` script.

Please note, that in case only the possibility of initialization of the `SmartAccount` implementation will be banned it will be possible to use this attack. This is so because in such a case `owner` variable will be equal to zero and it will be easy to pass a check inside of `checkSignatures` function using the fact that for incorrect input parameters `ecrecover` returns a zero address.

## Recommendation
Add to the deploy script initialization of the `SmartAccount` implementation, or add to the `SmartAccount` contract the following constructor that will prevent implementation contract from the initialization:
    
    // Constructor ensures that this implementation contract can not be initialized
    constructor() public {
        owner = address(1);
    }

[#14](https://github.com/code-423n4/2023-01-biconomy-findings/issues/14) also notes that if owner is left to address(0) some validation can be bypassed.
