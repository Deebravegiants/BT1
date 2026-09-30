# [H] Potential Exploits from Guardian Role

## Summary
Severity: High
Contest weight: 0.3789
Dataset id: 14144
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Angle’s threat model includes two main types of permissioned users, Guardians and Governors. The Governor role will be controlled by a DAO and will have the highest level of permissions, allowing direct withdrawal of funds from the protocol. The Guardian role is intended to be a multisig account owned by core developers and potentially trusted third parties which can be used to act quickly in case of an attack.
The Guardian role should not be allowed to directly withdraw funds from the protocol. However, there are four potential ways for the Guardian role to exploit its privileges to withdraw funds from the protocol:
• The first attack vector available to a Guardian is through the PoolManager.addStrategy() function. The PoolManager will transfer a large proportion of the funds owned by the protocol to a Strategy. The Guardian is allowed to add any arbitrary address as a new Strategy which will receive the protocols collateral tokens as an investment. Hence, they may add a malicious contract as the new strategy which receives tokens from the protocol then transfers these tokens to an attacker owned address.
• The second and third attack vectors are from manipulating the price by setting malicious oracles in the functions StableMaster.setOracle() and BondingCurve.changeOracle():
  – Manipulating the oracle price in StableMaster could be exploited from a malicious user by taking out a large position in the PerpetualManager. Then using a malicious oracle to increase the price exponentially. This would increase the attackers cashOutAmount in the perpetual swap enough that they could withdraw all the collateral tokens in the protocol.
  – Similarly by setting an advantageous price in BondingCurve they could buy tokens for significantly less than what they are worth.
• Finally, a Guardian may extract all of the funds from the RewardsDistributor through the function setStakingContract(). This allows the Guardian to specify a contract to receive reward tokens and the amount of tokens that will be sent. By setting the staking contract to a malicious address, the Guardian could withdraw all reward tokens from the RewardsDistributor.

## Recommendation
Consider updating these functions to only be allowed to be called by accounts with the Governor role, thereby preventing misuse or malicious use by Guardians.
