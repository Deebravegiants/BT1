# [M] Changing `atomWarden` will result in losing `atomWalletInitialDepositAmount` for Created and not Deployed Atoms

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-25
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/50
Type: hats-finding

## Details
**Github username:** @Al-Qa-qa
**Twitter username:** al_qa_qa
**Submission hash (on-chain):** 0xc518fa0e591487973f4d31750e421dc652b1ae07f42aee2489353a9ea1ea9f70
**Severity:** medium

**Description:**
**Description**\
When creating new Atom wallets, there are two processes. First, is the creation of the atom vault. Second, is deploying the wallet.

When creating atom, `atomWalletInitialDepositAmount` goes to the atom wallet address that will be deployed using the current ID.


[EthMultiVault.sol#L481-L488](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/EthMultiVault.sol#L481-L488)
```solidity
        address atomWallet = computeAtomWalletAddr(id);

        // deposit atomWalletInitialDepositAmount amount of assets and mint the shares for the atom wallet
        _depositOnVaultCreation(
            id,
            atomWallet, // receiver
            atomConfig.atomWalletInitialDepositAmount
        );
```  

When creating `atomWallet` address that will receive the initialDeposit, it is calculating using the current args, and `atomWarden` is one of the args.

[EthMultiVault.sol#L1421-L1423](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/EthMultiVault.sol#L1421-L1423)
```solidity
        bytes memory initData = abi.encodeWithSelector(
@>          AtomWallet.init.selector, IEntryPoint(walletConfig.entryPoint), walletConfig.atomWarden, address(this)
        );
```

But in case of deploying, we recompute this address again.

[EthMultiVault.sol#L366](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/EthMultiVault.sol#L366)
```solidity
    function deployAtomWallet(uint256 atomId) external whenNotPaused returns (address) {
        if (atomId == 0 || atomId > count) {
            revert Errors.MultiVault_VaultDoesNotExist();
        }

        // compute salt for create2
        bytes32 salt = bytes32(atomId);

        // get contract deployment data
@>      bytes memory data = _getDeploymentData();
        ...
        assembly {
            atomWallet := create2(0, add(data, 0x20), mload(data), salt)
        }
        ...
    }
```

So all AtomVaults that did not deployed there Wallets, will not be able to claim their initialAmount, if the `atomWarden` changed.

**Senario**\

- UserA Created atom wallet
- After a while, the team changed `atomWarden` using `setAtomWarden`
- UserA deployed his AtomWallet using its vault ID, but the address is totally different from the one the received `InitialDepositAmount`


**Recommendations**\

In case of changing AtomWarden, you need to check that all created atoms gets deployed. this can either be done on-chain,  or off-chain.
