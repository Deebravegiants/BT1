No vulnerability found for this question.

**Analysis:**

The `vest` function's period math is straightforward integer division with no overflow/underflow risk, and no unprivileged attacker can manipulate `timestamp::now_seconds()`.

1. **No overflow/underflow in period calculation.** `last_completed_period = (timestamp::now_seconds() - vesting_schedule.start_timestamp_secs) / vesting_schedule.period_duration` is only reached after the guard `vesting_contract.vesting_schedule.start_timestamp_secs > timestamp::now_seconds()` returns early, so the subtraction never underflows. [1](#0-0) 

2. **Period advances by exactly one per call, never more.** `next_period_to_vest = last_vested_period + 1` and `vesting_schedule.last_vested_period = next_period_to_vest` — regardless of how far `last_completed_period` has advanced past `next_period_to_vest`, only a single period's fraction is vested per call. If multiple periods have elapsed without a `vest` call, subsequent calls will each process one period in sequence, which is the intended catch-up behavior, not an exploit. [2](#0-1) 

3. **Distribution is hard-capped.** `vested_amount = min(vested_amount, vesting_contract.remaining_grant)` guarantees `remaining_grant` can never go negative or below zero (it is a `u64`, so underflow would abort in Move regardless), and total unlocked across all calls can never exceed the original grant. [3](#0-2) 

4. **Exact boundary behavior is correct.** At `now_seconds() - start == period_duration * k`, `last_completed_period` correctly equals `k`, meaning period `k` has genuinely completed — this is expected, not an off-by-one bug.

5. **The premise itself is out of the review's scope.** `timestamp::now_seconds()` is the on-chain block timestamp set by validators during block prologue (a privileged, consensus-controlled path), not something an unprivileged caller can set to an arbitrary "manipulated" value. Any scenario requiring timestamp manipulation falls under "malicious node/validator behavior," which is explicitly excluded from this review's bounds.

Since the arithmetic is monotonic, guarded against underflow, and capped by `remaining_grant`, and since the premise requires a privileged validator action to manipulate the timestamp, there is no valid custody-boundary crossing here.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L662-693)
```text
        // Short-circuit if vesting hasn't started yet.
        if (vesting_contract.vesting_schedule.start_timestamp_secs > timestamp::now_seconds()) {
            return
        };

        // Check if the next vested period has already passed. If not, short-circuit since there's nothing to vest.
        let vesting_schedule = &mut vesting_contract.vesting_schedule;
        let last_vested_period = vesting_schedule.last_vested_period;
        let next_period_to_vest = last_vested_period + 1;
        let last_completed_period =
            (timestamp::now_seconds() - vesting_schedule.start_timestamp_secs) / vesting_schedule.period_duration;
        if (last_completed_period < next_period_to_vest) {
            return
        };

        // Calculate how much has vested, excluding rewards.
        // Index is 0-based while period is 1-based so we need to subtract 1.
        let schedule = &vesting_schedule.schedule;
        let schedule_index = next_period_to_vest - 1;
        let vesting_fraction = if (schedule_index < schedule.length()) {
            schedule[schedule_index]
        } else {
            // Last vesting schedule fraction will repeat until the grant runs out.
            schedule[schedule.length() - 1]
        };
        let total_grant = vesting_contract.grant_pool.total_coins();
        let vested_amount = fixed_point32::multiply_u64(total_grant, vesting_fraction);
        // Cap vested amount by the remaining grant amount so we don't try to distribute more than what's remaining.
        vested_amount = min(vested_amount, vesting_contract.remaining_grant);
        vesting_contract.remaining_grant -= vested_amount;
        vesting_schedule.last_vested_period = next_period_to_vest;
        unlock_stake(vesting_contract, vested_amount);
```
