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

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/37_
