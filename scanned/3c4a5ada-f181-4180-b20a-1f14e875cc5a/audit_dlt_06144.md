# [M] Shares can be transferred to un-whitelisted accounts in `EthPrivErc20Vault.sol`

## Summary
Severity: Medium
Chain: Smart contract
Component: StakeWise
Published: 2023-08-22
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/39
Type: hats-finding

## Details
**Github username:** @milotruck
**Submission hash (on-chain):** 0x8d2352dc289982ddbdc1e8054321b700ae83cfdb387dd32cd47a848bc8b14d2e
**Severity:** medium

**Description:**
## Bug Description

In `EthPrivErc20Vault.sol`, the vault admin has full control over which addresses can deposit/withdraw ETH from the vault. This can be seen in the [documentation](https://docs-v3.stakewise.io/protocol-overview-in-depth/vaults#whitelist):

> Whitelist is a function in Private Vaults that allows Vault Admin to control who can deposit and withdraw ETH from the Vault. 

This is enforced using a whitelist, as seen in `deposit()`:

[EthPrivErc20Vault.sol#L78-L86](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/ethereum/EthPrivErc20Vault.sol#L78-L86)

```solidity
  function deposit(
    address receiver,
    address referrer
  ) public payable virtual override(IVaultEthStaking, VaultEthStaking) returns (uint256 shares) {
    if (!(whitelistedAccounts[msg.sender] && whitelistedAccounts[receiver])) {
      revert Errors.AccessDenied();
    }
    return super.deposit(receiver, referrer);
  }
```

As seen from above, the function checks that `receiver` is whitelisted in `whitelistedAccounts`. This allows the vault's admin to have full control over which address holds shares using the whitelist.

However, the `transfer()` and `transferFrom()` functions do not validate that the receiving address is whitelisted. This allows users to bypass the whitelist and transfer shares to un-whitelisted addresses, for example:

- Assume that Alice is whitelisted in an `EthPrivErc20Vault` vault.
- Bob, a friend of Alice, wants to deposit assets into the private vault, but he is not whitelisted.
- Alice receives ETH from Bob and calls `deposit()` on his behalf.
- After shares are minted to her, she calls `transfer()` to transfer the shares to Bob.

In this scenario, although Bob is not whitelisted by the vault's admin, he now holds shares and can earn yield from the vault, and can call the vault's other functions, such as `redeem()`.


_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/39_
