# [M] M-03 | Users Should Ensure They Hold Only esGMX Before Deploying A Vault To Optimize Gains

## Summary
Severity: Medium
Contest weight: 0.4645
Dataset id: 2045
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To deploy an ExitVault contract the user must perform a full account transfer. This process transfers all tokens and stakes associated with the user's GMX protocol account into the vault, including any staked GMX, esGMX, and other tokens. For instance, if a user has staked 1000 GMX tokens and has earned 100 esGMX tokens that they wish to convert through the vault, initiating the vault deployment and performing the account transfer moves all these assets into the vault. Once the vault holds the staked GMX and the esGMX tokens, it can immediately use the staked GMX to unlock the esGMX without needing additional participants. This renders the collaborative aspect of the vault pointless, as the vault no longer requires contributions from other users to maximize its vesting capacity. Moreover, the user's staked GMX and other tokens are now locked within the vault and the user loses direct operational control over them. They cannot claim rewards, adjust their staking positions, or interact with their tokens outside the vault. To regain access and control, the user would need to exit the vault by performing another full account transfer, which can only be done after a year due to the vesting period. This situation may lead vault creators to inadvertently lock up their staked tokens and lose flexibility in managing their assets, contrary to their intentions. It also negates the primary purpose of the vault system, which is to pool resources from multiple users to collectively unlock esGMX tokens, maximizing gains through collaboration. By having sufficient GMX within the vault to unlock the esGMX independently, the need for other users to participate is eliminated.

## Recommendation
Ensure that this behavior is documented and known by the users before deploying a vault. To optimize gains and maintain control over their assets, users should ensure they hold only esGMX tokens before deploying a vault. Prior to initiating the vault deployment and account transfer, users should unstake their GMX tokens and withdraw any other staked assets, leaving only the esGMX tokens in their account. By doing so, when they perform the account transfer to the vault, only the esGMX tokens are moved, and the vault will not have sufficient GMX to unlock the esGMX on its own. This preserves the need for collaborative participation, allowing multiple users to contribute GMX to the vault to maximize vesting capacity collectively. On the other hand, consider adding the following require statement in the ExitVault.initialize function to prevent the described scenario:
```solidity
uint256 totalGMXGLP = IStakedGmx(TOKEN_STAKED_GMX).depositBalances(address(this), TOKEN_GMX) +
IERC20(TOKEN_STAKED_GLP).balanceOf(address(this));
require(totalGMXGLP < stakedEsGmxBalance);
```
