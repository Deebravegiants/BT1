# [M] withdraw can fail unexpectedly

## Summary
Severity: Medium
Reporter: Amaechi Okolobi, also found by zigtur and Koolex
Contest weight: 0.1753
Dataset id: 4810
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Lockbox::withdraw the call can revert unexpectedly due to a missing call to whirlpool::collect_rewards. The function first calls whirlpool::cpi::update_fees_and_rewards(cpi_ctx_update_fees)?; This calls the following code in whirlpool: let (position_update, reward_infos) = calculate_fee_and_reward_growths(whirlpool, position, &ctx.accounts.tick_array_lower, &ctx.accounts.tick_array_upper, timestamp, )?; whirlpool.update_rewards(reward_infos, timestamp); position.update(&position_update); This will apply rewards in certain cases. The issue is that the withdraw function doesn't then call whirlpool::collect_rewards, meaning the position may still have rewards. If this is the case then the whirlpool::cpi::close_position(cpi_ctx_close_position)?; will fail due to this check: if !Position::is_position_empty(&ctx.accounts.position) { return Err(ErrorCode::ClosePositionNotEmpty.into()); } Which executes the following check here: pub fn is_position_empty<'info>(position: &Position) -> bool { let fees_not_owed = position.fee_owed_a == 0 && position.fee_owed_b == 0; let mut rewards_not_owed = true; for i in 0..NUM_REWARDS { rewards_not_owed = rewards_not_owed && position.reward_infos[i].amount_owed == 0 } position.liquidity == 0 && fees_not_owed && rewards_not_owed }

## Recommendation
Call whirlpool::collect_rewards before closing the position.
