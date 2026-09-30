# [M] Protocol admin is a single point of failure.

## Summary
Severity: Medium
Contest weight: 0.2690
Dataset id: 17478
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Protocol admin can arbitrarily and unilaterally list vaults/options, update vault/call factory addresses, configure the market/collection parameters and pause/unpause the markets/protocol. This presents a critical single point of failure.
Hook protocol uses OpenZeppelin’s AccessControl.sol to implement role-based access control (RBAC) with seven different roles: ADMIN_ROLE, ALLOWLISTER_ROLE, PAUSER_ROLE, VAULT_UPGRADER, CALL_UPGRADER, MARKET_CONF and COLLECTION_CONF. specific timelocks or other safety measures. The roles are granted with the principal of least privilege. As the protocol matures, these additional measures can be layered by granting these roles to other contracts. In the extreme, the upgrade and other roles can be burned, which would effectively make the protocol static and non-upgradeable.”
However, the initial configuration assigns the admin address to all the seven roles thereby defeating the motivation behind separation of roles. If a protocol admin becomes malicious or compromised, the entire protocol is immediately at risk for all existing/future markets/participants. While the updation of many critical parameters emit events, that only lets market participants react after the fact because these changes are not time-delayed.
A scenario that affects future markets/participants is the updation of vault/call factory addresses to malicious ones. Neither of these actions emit events and will go unnoticed by option writers/holders/bidders.
A DoS scenario, for existing markets/participants, is the protocol admin, in the MARKET_CONF role, setting the minimumOptionDuration, newSettlementStartOffset or minBidIncrementBips to unreasonable values which prevents the expected functioning of covered call option markets. The admin in the COLLECTION_CONF role can disable airdrops, flash loans and execTransaction capability of solo vaults which may cause DoS for certain assets and actions.

## Recommendation
configuration is part of the guarded launch strategy, the protocol admin should nevertheless be a reasonable threshold multisig (e.g. 4/7, 5/9) with diverse owners and (cold/hardware) wallets until it is backed by token-holder governance, i.e., it should certainly never be an EOA. The highest possible operational security measures should be taken for all multisig owners and wallets.
The assignment of roles to and management by different addresses should be enforced at the earliest in the spirit of the Principle of Least Privilege and Principle of Separation of Privilege.
Use the separate address in the protocol constructor for ALLOWLISTER, PAUSER, VAULT_UPGRADER, CALL_UPGRADER, MARKET_CONF, and COLLECTION_CONF instead of a single admin address.
https://github.com/hookart/protocol/pull/55
Ok. To enforce that addresses are really different, we can add a != check in the constructor on the seven input parameters.
