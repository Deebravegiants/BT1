# [M] Incorrect deployment parameters

## Summary
Severity: Medium
Contest weight: 0.0879
Dataset id: 9692
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an outdated deployment parameter in the scripts that initialise the protocol. Specifically, the address of the G‑Uni liquidity‑provider (LP) token hard‑coded in the configuration file does not match the current LP token contract that distributes yield. This mismatch is a classic case of configuration or deployment mis‑parameterisation, where a constant value was never refreshed after an upgrade of the underlying token contract. Because the staking contract references the wrong token address, any funds users deposit are effectively locked in a contract that no longer issues rewards. Consequently, users see no increase in their balances, no pending rewards appear on the UI, and the expected yield is absent despite successful staking transactions. The issue manifests whenever the protocol is deployed using the stale scripts, regardless of the network, and affects every participant who interacts with the staking functionality – from casual users to protocol engineers. It was discovered during a manual audit of the deployment files, where the auditor compared the address in the script against the address reported by the live staking contract and identified a discrepancy. The problem is subtle because the front‑end displays the correct pair symbols and transaction receipts report success, so the failure is only observable through missing rewards or unchanged balances, which can be mistakenly attributed to market conditions. To remediate, the deployment process should retrieve the LP token address directly from the staking contract at deployment time or the configuration file must be updated to contain the current, verified address before any contracts are published. This correction restores the intended accounting logic, ensuring that deposited assets are linked to the proper reward‑generating contract and that users receive the yield they expect.

## Proof of Concept
For example for agEUR/USDC it is 0xedecb43233549c51cc3268b5de840239787ad56c and not 0x2bD9F7974Bc0E4Cb19B8813F8Be6034F3E772add.

## Recommendation
For safety why not fetching directly the LP token from the staking contract?

The warden has shown how a configuration file shows that the settings for the project are using an old address.

While the finding pertains to a setup script (generally out of scope), given that:

  * The sponsor has confirmed
  * The finding is valid in that using older deployments will cause at the very least a loss of yield
  * We already had an instance of bringing an out-of-scope file into scope via Sponsor-Confirming (See: [#209](https://github.com/code-423n4/2022-05-vetoken-findings/issues/209))


With the information I have, I believe the finding to be of Medium Severity and believe the sponsor will mitigate by updating to the Warden suggested addresses.
