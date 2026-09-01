# [H] Rounding Issue in Reward Rate Could Result in Less Rewards for Users

## Summary
Severity: High
Chain: Smart contract
Component: AlephZeroAMM
Published: 2024-01-26
Source: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/44
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x6922988f960a847014c23ddb769f4eb89978514ee91c64dbe36d050ccee39040
**Severity:** high

**Description:**
**Description**

The reward rate is calculated in the following way:

```rust
                let reward_rate = reward_amount
                    .checked_div(duration)
                    .ok_or(FarmError::ArithmeticError(MathError::DivByZero(3)))?;
```
After that, the reward_rate will be used in the following way:
```rust
casted_mul(reward_rate, time_delta)
    .checked_mul(U256::from(SCALING_FACTOR))
    .ok_or(MathError::Overflow(1))?
    .checked_div(U256::from(total_shares))
    .ok_or(MathError::DivByZero(1))
```

There is a hidden division before multiplication here, which will cause fewer rewards for users.

**Secnario**  

Owner wants to start a farm with a reward token A. The owner starts a new farm for about 1 month with 1000 USDC. The reward rate is calculated as follows:

```
reward rate = (1000 * 10^6 /(8640*1000*30*1)) = 3.8580
```

But, as there are no floating numbers, the reward rate will be 3. Here, I will calculate for 1 month:

```
3 * (8640*1000*30*1) = 777,600,000
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/44_
