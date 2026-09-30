# [C] Multiple staking_states can be created for the same stake-mint, letting attackers steal rewards and principal

## Summary
Severity: Critical
Contest weight: 0.3501
Dataset id: 9044
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In IndexTokenStaking, the pool state (staking_state) is keyed by both the stake‑token mint and the pool authority, so anyone can initialize parallel pools that accept the same token but track rewards separately. By contrast, a user’s position (user_staking_account) is keyed only by the mint and the user’s key, so that a single PDA is silently shared across every staking_state built on the same token.
https://github.com/OpenDeltaLabs/index_token_staking_audit/blob/main/programs/index_token_staking/src/instructions/stake.rs#L61C9-L61C98:
```
// staking_state-specific
seeds = [STAKING_STATE_SEED, stake_token_mint.key().as_ref(),
authority.key().as_ref()],
]
https://github.com/OpenDeltaLabs/index_token_staking_audit/blob/main/programs/index_token_staking/src/instructions/stake.rs#L40:
// user position  (authority missing)
seeds = [USER_STAKING_ACCOUNT_SEED, stake_token_mint.key().as_ref(),
user.key().as_ref()],
]
```
Because deposits made in one staking_state increase user_staking_account.staked_amount for all staking_states while only the local total_staked is updated, an attacker can over‑state their stake in a victim staking_state, drain its reward vault, and make staking_states insolvent.
If two states share the same stake mint, an attacker is able to call unstake() in pool A (which internally uses the correct staking_state); then call withdraw_stake() but pass the vault of pool B.
Because withdraw_stake() does not verify that the supplied staking_state matches the vault it debits, the attacker successfully pulls tokens from B’s vault, leaving pool A insolvent for honest stakers.
#### Steps to Reproduce
Reward-vault drainage:
1. Alice initializes pool P₀ with authority = Alice.
2. Bob initializes pool P₁ with the same stake_token_mint but authority = Bob.
3. Bob stakes N tokens in P₁; user_staking_account.staked_amount becomes N.
4. Bob calls claim_rewards/withdraw_rewards on P₀. P₀ uses the bloated staked_amount with its smaller total_staked, over‑paying Bob.
Cross-pool principal theft / Insolvency
1. Attacker calls unstake in pool A; A’s staking_state is updated correctly.
2. Attacker calls withdraw_stake but supplies B’s vault and B-specific accounts.
3. Because withdraw_stake never checks that the vault matches the supplied staking_state, tokens are pulled from B’s vault.
4. Pool A now shows the position closed while pool B has lost funds, leaving honest stakers under-collateralised.

## Recommendation
Bind each user position to a single pool by including the the staking_state's key in the PDA seeds:
```
#[account(
    init,
    payer = user,
    space = 8 + std::mem::size_of::<UserStakingAccount>(),
    // the user staking account must encode the staked token mint and the users public key.
    seeds = [USER_STAKING_ACCOUNT_SEED, stake_token_mint.key().as_ref(),
        user.key().as_ref(),
        +staking_state.key().as_ref(),
    ],
    bump
)]
pub user_staking_account: Account<'info, UserStakingAccount>,
```
