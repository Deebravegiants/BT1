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

Now, an owner wants to give 1000 USDC, but the actual reward is 777 USDC.

If we use a scale factor for the reward rate to prevent division before multiplication:

```
reward rate = (1000 * 10^6 * [10^6] /(8640*1000*30*1)) = 3,858.024
```

But, as there are no floating numbers, the reward rate will be 3858. Here, I will calculate for 1 month and divide by the scale factor:

```
3858 * (8640*1000*30*1) / 10^6 = 999,993
```

As you can see, the error increases from 233 to 7. If we use a bigger scale factor, the error will increase even more.

**Impact**

Users will get fewer rewards than the farmer intends to distribute.

**Proof of Concept**
Add the following test:

```rust
#[drink::test]
fn reward(){
    // initialize the session
    let mut session: Session<MinimalRuntime> = Session::new().expect("Init new Session");

    // set up the necessary tokens (ICE(lp), WOOD(reward)
    let ice = setup_psp22(&mut session, ICE.to_string(), ICE.to_string(), BOB);
    let wood = setup_psp22(&mut session, WOOD.to_string(), WOOD.to_string(), BOB);

    // set up the farm with ICE as the pool token and WOOD as a reward token
    let farm = setup_farm(
        &mut session,
        ice.into(),
        vec![wood.into()],
        BOB,
    );

    // deposits lp token
    let deposit_amount = 1000000;
    increase_allowance(&mut session, ice.into(), farm.into(), deposit_amount, BOB).unwrap();
    let call_result = deposit_to_farm(
    &mut session,
    &farm,
    deposit_amount,
    BOB);
    assert!(call_result.is_ok());

    // setting up start, end and the rewards amount
    let now =  get_timestamp(&mut session);
    let farm_start = now;
    let farm_end = farm_start + 259200000; //1 MONTH (30 days * 24 hours * 60 min * 60 sec * 1000 millisecond)
    let rewards_amount = 1000000000 ; // USDC 1000

    // increasing allowance for the reward token
    increase_allowance(&mut session, wood.into(), farm.into(), rewards_amount, BOB).unwrap();

    // starting the new farm
    let call_result = setup_farm_start(
        &mut session,
        &farm,
        farm_start,
        farm_end,
        vec![rewards_amount],
        BOB,
    );
    assert!(call_result.is_ok());

    // set timestamp to farm end so users earn some reward in this farm but AND contract has balance
    set_timestamp(&mut session, farm_end);

    let bob_wood_balance_before = balance_of(&mut session, wood.into(), bob());
    
    // Attempt to withdraw tokens rewards from the contract
    let call_result = owner_withdraw(
        &mut session,
        &farm,
        wood.into(),
        BOB,
    );
    assert!(call_result.is_ok());

    let bob_wood_balance_after = balance_of(&mut session, wood.into(), bob());

    assert_eq!(bob_wood_balance_after - bob_wood_balance_before , 0)

}
```

Modify setup_psp22 as well in utils.rs to show USDC example:

```diff
pub fn setup_psp22(
    session: &mut Session<MinimalRuntime>,
    name: String,
    symbol: String,
    caller: drink::AccountId32,
) -> PSP22 {
    let _code_hash = session.upload_code(psp22::upload()).unwrap();

    let _ = session.set_actor(caller);

    let instance = PSP22::new(
        SCALING_FACTOR,
        Some(name),
        Some(symbol),
+        6,
    );
```

Output:

```rust
running 1 test
thread 'tests::reward' panicked at 'assertion failed: `(left == right)`
  left: `222400000`,
 right: `0`', src/tests.rs:419:5
```
As you see, owenr get 222 USDC. So 1000_000_000 - 222_400_000 = 777600000. Users get 777 USDC instead of 1000 USDC.


**Recommended Mitigation**

Use a scale factor in the calculation of the reward rate in the assert_start_params function.
