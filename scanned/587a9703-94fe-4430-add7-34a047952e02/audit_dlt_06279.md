# [H] Risk of Unintentional or Intentional User Rewards Prevention by Farm Contract Owner

## Summary
Severity: High
Chain: Smart contract
Component: AlephZeroAMM
Published: 2024-01-19
Source: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/10
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xfde1e9599918b97294459a45717d1e565040ae24f105c21ba9e8d412041f6953
**Severity:** high

**Description:**
**Description**\

In the farm contract, the farm contract owner can unintentionally or Intentionally prevent users from claiming granted rewards. The issue arises when attempting to withdraw tokens while the farm is inactive. The current check has a flaw; the check passes if the farm is set for the future. As a result, users' unclaimed rewards update in the future, but without actual reward tokens in the contract, the `claim_rewards` function fails, preventing users from retrieving even their previous rewards.

**Impact**\
One of the important roles in a farm contract is that the owner isn't able to steal or prevent users from claiming granted rewards.
In the following Scenario, users aren't able to get their granted rewards.

**Scenario**\
Consider the following scenario:

- User A has unclaimed rewards (e.g., 100 tokens) in the contract.
- The owner initiates a new farm for the future.
- The owner withdraws tokens while the farm is inactive.
- The farm becomes active, and User A earns new rewards (e.g., 50 tokens).
- When User A attempts to claim rewards, only the previous 100 tokens are available in the contract, leading to the failure of the claim_rewards function.


**Attachments**

1. **Proof of Concept (PoC) File**
Add the following functions to utils.rs:

```rust
pub fn deposit_to_farm(
    session: &mut Session<MinimalRuntime>,
    farm: &Farm,
    amount: u128,
    caller: drink::AccountId32,
) -> Result<()> {
    let _ = session.set_actor(caller);

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/10_
