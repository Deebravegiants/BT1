# [M] Reverting when the AA Wallet is already deployed violates ERC4337

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-27
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/57
Type: hats-finding

## Details
**Github username:** @Al-Qa-qa
**Twitter username:** al_qa_qa
**Submission hash (on-chain):** 0x36e29ca734d41d7c5b1ad387c553567829edc763f4e2e19633f64d7886154c98
**Severity:** medium

**Description:**
**Description**\
We we deploy our AA Atom wallets using EthMultiVault (SingleTone), we are reverting the transaction if the result was `address(0)`.

[EthMultiVault.sol#L375-L381](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/EthMultiVault.sol#L375-L381)
```solidity
        assembly {
            atomWallet := create2(0, add(data, 0x20), mload(data), salt)
        }

        if (atomWallet == address(0)) {
            revert Errors.MultiVault_DeployAccountFailed();
        }
```

This will occur (returning `0`) in case of hash collision, or the contract is already deployed.

The problem lies is that according to ERC4337, the SingleTone Factory, which is the contract that is used to create AA wallets, should not revert when deploying an already existed Wallet, and instead it should return the AA address.


[EIP4337#first-time-account-creation](https://eips.ethereum.org/EIPS/eip-4337#first-time-account-creation)

> **`it’s expected to return the wallet address even if the wallet has already been created`**. This is to make it easier for clients to query the address without knowing if the wallet has already been deployed, by simulating a call to `entryPoint.getSenderAddress()`, which calls the factory under the hood

As stated in the EIP, this helps Clients in simulation process, when doing transaction from a `counterfactional` wallet, and besides this, It is not the standard way.

**Recommendations**\

Return the address of the Atom wallet if it is already existed, and the deployment process failed.

> EthMultiVault::deployAtomWallet()
```diff
        if (atomWallet == address(0)) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/57_
