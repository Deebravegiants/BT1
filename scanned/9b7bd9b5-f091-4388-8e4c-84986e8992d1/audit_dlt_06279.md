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

    session
        .execute(farm.deposit(amount))
        .unwrap()
        .result
        .unwrap()
        .unwrap();

    Ok(())
}

pub fn owner_withdraw(
    session: &mut Session<MinimalRuntime>,
    farm: &Farm,
    token: AccountId,
    caller: drink::AccountId32,
) -> Result<()> {
    let _ = session.set_actor(caller);

    session
        .execute(farm.owner_withdraw_token(token))
        .unwrap()
        .result
        .unwrap()
        .unwrap();

    Ok(())
}
```

Include the following test in tests.rs:

```rust
#[test]
fn test_test() {
    // Initialize the session
    let mut session: Session<MinimalRuntime> = Session::new().expect("Init new Session");

    // Set up the necessary tokens (ICE(lp), WOOD(reward))
    let ice = setup_psp22(&mut session, ICE.to_string(), ICE.to_string(), BOB);
    let wood = setup_psp22(&mut session, WOOD.to_string(), WOOD.to_string(), BOB);
    let sand = setup_psp22(&mut session, SAND.to_string(), SAND.to_string(), BOB);

    // Set up the farm with ICE as the pool token and WOOD and SAND as reward tokens
    let farm = setup_farm(
        &mut session,
        ice.into(),
        vec![wood.into(), sand.into()],
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


    // Start the first farm
    let now =  get_timestamp(&mut session);
    set_timestamp(&mut session, now);
    let farm_start = now;
    let farm_end = farm_start + 100;
    let rewards_amount = 100000000000000;
    increase_allowance(&mut session, wood.into(), farm.into(), rewards_amount, BOB).unwrap();
    increase_allowance(&mut session, sand.into(), farm.into(), rewards_amount, BOB).unwrap();
    let call_result = setup_farm_start(
        &mut session,
        &farm,
        farm_start,
        farm_end,
        vec![rewards_amount, rewards_amount],
        BOB,
    );
    assert!(call_result.is_ok());

    // set timestamp to farm end so users earn some reward in this farm but AND contract has balance
    set_timestamp(&mut session, farm_end);

    // Start a new farm for the future
    let new_farm_start = farm_end + 200;
    let new_farm_end = new_farm_start + 100;
    let bob_wood_balance_before = balance_of(&mut session, wood.into(), bob());

    increase_allowance(&mut session, wood.into(), farm.into(), rewards_amount, BOB).unwrap();
    increase_allowance(&mut session, sand.into(), farm.into(), rewards_amount, BOB).unwrap();
    let call_result = setup_farm_start(
        &mut session,
        &farm,
        new_farm_start,
        new_farm_end,
        vec![rewards_amount, rewards_amount],
        BOB,
    );
    assert!(call_result.is_ok());

    // Attempt to withdraw tokens rewards from the contract
    let call_result = owner_withdraw(
        &mut session,
        &farm,
        wood.into(),
        BOB,
    );
    assert!(call_result.is_ok());

    // set timestamp to new farm end so users earn some reward in this new farm but no rewards are in contract
    set_timestamp(&mut session, new_farm_end);

    // Attempt to claim rewards, expecting it to fail
    let Error =
        farm::FarmError::TokenTransferFailed(wood.into(), farm::PSP22Error::InsufficientBalance());
    let call_result = session
            .query(farm.claim_rewards([0].to_vec()))
            .unwrap()
            .result
            .unwrap();

    assert!(call_result == Err(Error));
}
```

2. **Revised Code File (Optional)**
there will be more intelligent decisions for this, but as for now, I recommend this one:
in `owner_withdraw_token` instead of checking `!self.is_active()`, call `owner_stop_farm`.
