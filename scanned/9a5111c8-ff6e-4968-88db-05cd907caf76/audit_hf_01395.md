# [M] Centralization Risk Due to Trusted Owner

## Summary
Severity: Medium
Contest weight: 0.1873
Dataset id: 7139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract has an owner with the privileged right to pause and unpause most of the contract’s
functionality and therefore it needs to be trusted. Currently, the contract owner is not prevented
from renouncing the ownership while the contract is paused, which could cause any user assets
stored in the protocol, to be locked indefinitely.
Both Dark Mythos and Shieldify have been clear from the get-go that this functionality was only im-
plemented because EU law (Article 30 of REPORT on the proposal for a regulation) currently requires
that a mechanism exists to terminate the continued execution of transactions. Nonetheless, Dark Mythos kindly asked Shieldify to incorporate this (hopefully temporary) issue here in the
report to ensure Dark Myhtos’ users enjoy full transparency. Dark Mythos intends to keep this priv-
ileged role only as long as the legal situation is not fully clarified. Furthermore, Dark Mythos has
implemented a dedicated function to revoke their privileged role in the contract as soon as they
are certain that they don’t violate EU law by doing so. Dark Mythos will make an effort to investi-
gate this issue further and stay up to date with the latest legal developments.

## Recommendation
It is recommended that the client carefully manages the private key of the controller account to avoid
any potential hacking risk. Measures that can be taken are to enhance centralized privileges and
roles in the protocol through a decentralized mechanism or module-based accounts with enhanced
security practices. We propose to make the owner of DarkMythos a multi-sig wallet behind a Timelock
contract so that users can monitor what transactions are about to be executed by this account and
take action if necessary.
