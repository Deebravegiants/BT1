# [M] Upgrade-Safe Usage of SafeERC20 in CompoundVeFNXManagedNFTStrategyUpgradeable.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: Fenix-
Published: 2024-07-10
Source: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/31
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x4b5f4bccb1ff92e46d20f30d7d7af34c0e9e8b50f7a99d2d9930165e0c600861
**Severity:** medium

**Description:**
**Description**\

The current implementation of `CompoundVeFNXManagedNFTStrategyUpgradeable.sol` uses `SafeERC20` and `IERC20` from the non-upgradeable OpenZeppelin contracts. This can lead to potential issues when upgrading the contract due to the use of delegatecall in Address.sol, which SafeERC20 depends on. To ensure the contract is upgrade-safe, it is recommended to use SafeERC20Upgradeable and IERC20Upgradeable from the @openzeppelin/contracts-upgradeable repository.

https://github.com/OpenZeppelin/openzeppelin-upgrades/issues/455

**Attack Scenario**\
Describe how the vulnerability can be exploited.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
```
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
replace SafeERC20 with SafeERC20Upgradeable and IERC20 with IERC20Upgradeable to ensure the contract remains upgrade-safe.
