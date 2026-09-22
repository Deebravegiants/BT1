# [H] `mint_fee` collects fee from adding and removing liquidity

## Summary
Severity: High
Chain: Smart contract
Component: AlephZeroAMM
Published: 2024-01-22
Source: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/37
Type: hats-finding

## Details
**Github username:** @coreggon11
**Twitter username:** krikoeth
**Submission hash (on-chain):** 0xfa2f634e33a1c66390a57717bef271960460209ff9ecd5aab11e7bb43ebce999
**Severity:** high

**Description:**
**Description**\
The factory contract holds the information about [protocol fee benefeciary](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/main/amm/contracts/factory/lib.rs#L26). If this field is set to `Some(account)`, then the protocol should accrue [5 basis points fee](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/main/amm/contracts/pair/lib.rs#L25) from the trades, resulting in 16% of the pair fees to be sent to the protocol (`fee_to`).

However, there is a bug in the current implementation, which will result in not only a portion of the pair fees being sent to the fee beneficiary but also a significant portion of the liquidity added or removed.

**Attack Scenario**\
Bob provides liquidity for the first time. At the end of the call, `k_last` will be [updated](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/main/amm/contracts/pair/lib.rs#L351), but it will be set to `Some(0)` since it multiplies the members of a local tuple initialized [here](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/main/amm/contracts/pair/lib.rs#L305), which in the beginning is equal to `(0, 0)`.

Right after that, Bob will provide the same amount of liquidity (for the sake of this example, it can be any amount of liquidity). During `mint_fee`, the control flow goes to [this condition](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/main/amm/contracts/pair/lib.rs#L166), and since sqrt of `k_last` is 0, [this condition](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/main/amm/contracts/pair/lib.rs#L169) will be `true` as well. This will result in minting 16% more liquidity, with the overflowing liquidity being sent to the protocol fee collector, which will result in Bob being able to withdraw back significantly less than provided.

**Proof of Concept**
```Rust
#[test]
fn add_liquidity_collects_too_much_fee() {
    let mut session: Session<MinimalRuntime> = Session::new().expect("Init new Session");

    upload_all(&mut session);

    let fee_to_setter = bob();

    // initial amount of ICE is 2_000_000_000 * 10 ** 18
    let factory = setup_factory(&mut session, fee_to_setter);
    let ice = setup_psp22(&mut session, ICE.to_string(), BOB);
    let wood = setup_psp22(&mut session, WOOD.to_string(), BOB);
    let wazero = setup_wAzero(&mut session);
    let router = setup_router(&mut session, factory.into(), wazero.into());
    // feed charlie some native tokens
    session
        .sandbox()
        .mint_into(CHARLIE, 10u128.pow(12))
        .unwrap();

    // set fee collector to CHARLIE [3u8;32]
    session
        .execute(factory.set_fee_to(charlie()))
        .unwrap()
        .result
        .unwrap()
        .unwrap();

    let token_amount = 1_000_000_000 * 10u128.pow(18);
    increase_allowance(&mut session, ice.into(), router.into(), u128::MAX, BOB).unwrap();
    increase_allowance(&mut session, wood.into(), router.into(), u128::MAX, BOB).unwrap();

    let now = get_timestamp(&mut session);
    set_timestamp(&mut session, now);
    let deadline = now + 10;

    // bob mints the liquidity for the first time
    session
        .execute(router.add_liquidity(
            ice.into(),
            wood.into(),
            token_amount,
            token_amount,
            token_amount,
            token_amount,
            bob(),
            deadline,
        ))
        .unwrap()
        .result
        .unwrap()
        .unwrap();

    // bob mints the liquidity for the second time
    let (amount_ice, amount_wood, liquidity_minted) = session
        .execute(router.add_liquidity(
            ice.into(),
            wood.into(),
            token_amount,
            token_amount,
            0,
            0,
            bob(),
            deadline,
        ))
        .unwrap()
        .result
        .unwrap()
        .unwrap();

    let ice_wood_pair: pair_contract::Instance = session
        .query(factory.get_pair(ice.into(), wood.into()))
        .unwrap()
        .result
        .unwrap()
        .unwrap()
        .into();

    // since no swaps occured charlie (`fee_to`) should not have any liquidity
    // however we can see that he has 1/6th of the second liquidity
    let charlie_lp = session
        .query(ice_wood_pair.balance_of(charlie()))
        .unwrap()
        .result
        .unwrap();

    assert!(liquidity_minted == charlie_lp * 6);
}
```


**Recommended mitigation steps:**

Consider setting the k_last during `mint` and `burn` to the newly updated value.

Affected places: [mint](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/main/amm/contracts/pair/lib.rs#L351), [burn](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/main/amm/contracts/pair/lib.rs#L399)

```diff
    if fee_on {
-        self.pair.k_last = Some(casted_mul(reserves.0, reserves.1).into());
+       self.pair.k_last = Some(casted_mul(self.pair.reserve_0, self.pair.reserve_1).into());
    }
```
