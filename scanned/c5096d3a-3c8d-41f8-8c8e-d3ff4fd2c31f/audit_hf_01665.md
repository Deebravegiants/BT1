# [M] IDOPoolAbstract does not deal with yield and gas accrued on Blast

## Summary
Severity: Medium
Contest weight: 0.0372
Dataset id: 9016
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The IDOPoolAbstract contract is designed to hold stablecoins and native assets such as USDB, WETH and ETH for an IDO pool, but it does not contain any logic to interact with the Blast protocol’s reward system. Blast automatically generates yield on any contract that holds those assets and also allows contracts to claim a portion of the gas fees they have spent. Because IDOPoolAbstract never calls Blast’s claim functions, the accrued yield and refundable gas are never transferred to the pool’s balance. The root cause is a missing integration step: the contract assumes that the token balances it tracks are the only source of value, ignoring the external accounting that Blast maintains. This omission can be exploited indirectly by the protocol itself, as the unclaimed rewards remain locked in Blast and are effectively lost to the pool. The impact is financial rather than a classic security breach: participants in the IDO receive less than the expected return, the protocol’s revenue is reduced, and the overall economics of the offering become less attractive. The condition under which the problem manifests is any time the pool holds assets on a chain where Blast is active and accrues yield over time; the longer the assets sit, the larger the missed reward. All parties that rely on the pool’s funds – investors, token buyers, and the protocol’s treasury – are affected because the expected increase in balance never materialises. The issue was discovered during a systematic audit that compared the contract’s external dependencies against the documented capabilities of the underlying blockchain, revealing that the contract never invokes Blast’s reward‑claiming API. It is easy to overlook because the on‑chain token balances appear normal; the missing yield is invisible unless one explicitly checks Blast’s pending reward view. To remediate, the contract should be extended with functions that periodically query Blast for any pending yield or gas refunds and then call the appropriate claim methods, updating the pool’s internal accounting to reflect the newly received assets. In broader terms, this is a classic case of incomplete accounting for external incentive mechanisms, where a smart‑contract fails to capture all sources of value that its environment provides, leading to systematic under‑payment of participants.

## Recommendation
Implement functionality to deal with this yield and gas fees.
