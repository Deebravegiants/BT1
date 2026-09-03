# [M] No storage gap for the upgradable contracts

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-28
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/60
Type: hats-finding

## Details
**Github username:** @dinkras
**Twitter username:** dinkras
**Submission hash (on-chain):** 0xf858b671d16d9d90799812b4759408125cf81fb5309da6ccc29460e5a3246bd2
**Severity:** medium

**Description:**
**Description**\
**[AtomWallet.sol](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/AtomWallet.sol#L19) and [EthMultiWallet.sol](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/EthMultiVault.sol#L25)** are intended to be upgraded in the future via the Proxy pattern. However, no storage gap is present inside those contracts.

For upgradeable contracts, there must be a storage gap to "allow developers to freely add new state variables in the future without compromising the storage compatibility with existing deployments". Otherwise, it may be very difficult to write new implementation code and storage collisions may occur. 

Without a storage gap, the variable in the child contract might be overwritten by the upgraded base contract if new variables are added to the base contract. This could have unintended and very serious consequences for the child contracts.

**Attack Scenario**\
Scenario A
1) The protocol team has released a new version of **EthMultiVault** -> **EthMultiVaultV2** as shown as an example from the team here: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/test/EthMultiVaultV2.sol#L8
2. At some point the team has found a vulnerability in the base contract and releases a fix of  **EthMultiVault** which includes new/updated storage variables
3. The next deployments of **EthMultiVaultV2** will have storage collisions with the latest version of  **EthMultiVault** due to the missing storage gap

Scenario B
1) The protocol team decides **AtomWallet.sol** or **EthMultiWallet.sol** to inherit a new **contract B** which has a new storage variable
2) **Contract B** storage variable overrides the first storage slot variables of those contracts
3. Dev team deploys the new versions of the contracts
4. Storage collision occurs


**Attachments**

1. **Proof of Concept (PoC) File**
Same as the content inside the **Attack Scenario** section

2. **Revised Code File (Optional)**

**Recommendation**:
Introduce  storage gap/s insde AtomWallet.sol and EthMultiWallet.sol as recommended from the [OpenZeppelin docs](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable) (Storage Gaps section)


`uint256[gap_size] private __gap;`
