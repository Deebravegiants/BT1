# [H] New Users gain some rewards of old users

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-08-25
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/98
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Submission hash (on-chain):** 0x9217774ed6004486ed40e26ace76c7d6eaee3f015e2b1f8734d48dccb8f20b17
**Severity:** high

**Description:**
**Description**\
As mentioned in the docs:
- "Registering new validators in the Beacon Chain can take several weeks during times when many new staking deposits are being made. ETH staked in a Vault and used to create a validator will not start producing staking rewards until the validator passes the deposit queue and becomes active. This may cause a dilution in Vault's APY. "

But in the current implementation users can deposit ETH and start earning rewards even if their deposited ETH isn't used in Beacon Chain yet

**Impact**\

When someone deposits, it shouldn't take rewards until Registering new validators in the Beacon Chain which takes several weeks, but in the current implementation, users get some share of rewards.

**Attachments**

**Scenario**\

- User A deposits ETH
- After some time start earning rewards
- User B deposits ETH as well and starts earning from the reward of A's deposited ETH

**Revised Code File (Optional)**

Don't mint share until users deposit ETH used by validators in the Beacon Chain.
