# [M] Slashing process could be reverted

## Summary
Severity: Medium
Source: https://github.com/forta-protocol/forta-token/blob/92d7a7ddd6672a7530a4bfc532d0d697e7f12744/contracts/components/staking/FortaStaking.sol#L286
Type: audit-issue

## Details
When a certain subject under-performed or has done actions against the correct operation of the protocol, the `SLASHER_ROLE` role can slash that subject and all the users that have staked on it by calling the [slash function](https://github.com/forta-protocol/forta-token/blob/92d7a7ddd6672a7530a4bfc532d0d697e7f12744/contracts/components/staking/FortaStaking.sol#L286) from the `FortaStaking` contract. After the [value that should be taken from inactive and active stake is computed](https://github.com/forta-protocol/forta-token/blob/92d7a7ddd6672a7530a4bfc532d0d697e7f12744/contracts/components/staking/FortaStaking.sol#L299-L300), the slashed funds are [transferred to the \_treasury address](https://github.com/forta-protocol/forta-token/blob/92d7a7ddd6672a7530a4bfc532d0d697e7f12744/contracts/components/staking/FortaStaking.sol#L305).

However, if the `_treasury` address is being set as zero either during the [initialization](https://github.com/forta-protocol/forta-token/blob/92d7a7ddd6672a7530a4bfc532d0d697e7f12744/contracts/components/staking/FortaStaking.sol#L117) of the contract or by the `DEFAULT_ADMIN_ROLE` role with the [setTreasury function](https://github.com/forta-protocol/forta-token/blob/92d7a7ddd6672a7530a4bfc532d0d697e7f12744/contracts/components/staking/FortaStaking.sol#L493), the whole slashing mechanism will not work because the `FORT` token [does not allow to transfer tokens to the zero address](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/v4.4.2/contracts/token/ERC20/ERC20Upgradeable.sol#L233).

In order to prevent the possible reversion of the slashing process, consider always validating that the `_treasury` address is not zero when initializing the contract or when a new treasury address is being set.

_**Update:** Fixed on [commit b2c4d5aa398530d1ae5af14cf84eb438a377af5e in pull request 56](https://github.com/forta-protocol/forta-token/pull/56/commits/b2c4d5aa398530d1ae5af14cf84eb438a377af5e)._
