# [H] The owner of a farm can steal already accumulated rewards

## Summary
Severity: High
Chain: Smart contract
Component: AlephZeroAMM
Published: 2024-01-19
Source: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/20
Type: hats-finding

## Details
**Github username:** @coreggon11
**Twitter username:** krikoeth
**Submission hash (on-chain):** 0x1198b6c533d75e9d605e8bf0433c390a22e251d622bb963233c4313255b42759
**Severity:** high

**Description:**
**Description**\
The protocol states that users should be guaranteed that the rewards they have earned in the past can not be manipulated. However, it is possible for the owner of a farming pool to take out all the tokens out of the pool.

**Attack Scenario**\
A project owner will create a pool where users deposit `ICE` and they can get `WOOD`. Since there can be multiple reward tokens specified, the owner will specify the rewards as `[WOOD, WOOD]` when [creating the contract](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/0a7264d707aea51b559a1bf94448681b59660f6a/farm/contract/lib.rs#L80).

The owner will [start a new farm](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/0a7264d707aea51b559a1bf94448681b59660f6a/farm/contract/lib.rs#L282), specifying the start and end time, and setting the rewards as `[0, amount]`. `amount` here can be any desired amount,

Users will deposit their tokens and start farming the liquidity, and they will be happy about their returns. However, now the owner has stopped the farm. He should not be able to withdraw the rewards that users have accumulated. However, due to [this line](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/0a7264d707aea51b559a1bf94448681b59660f6a/farm/contract/lib.rs#L315) this will not be true. Since the reward for 0th token is 0, there is nothing accumulated in this token, and therefore, the undistributed balance will result in [total balance](https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/blob/0a7264d707aea51b559a1bf94448681b59660f6a/farm/contract/lib.rs#L320). However, there are rewards accumulated in this token on the 1st index of `farm_distributed_unclaimed_rewards`. Users will, however, not be able to withdraw them.


**Proof of Concept (PoC) File**

See the following test case:

```Rust
#[test]
fn deposit_after_farm_ends() {
    let mut session: Session<MinimalRuntime> = Session::new().expect("Init new Session");

    // inititate everything
    let ice = setup_psp22(&mut session, ICE.to_string(), ICE.to_string(), BOB);
    let wood = setup_psp22(&mut session, WOOD.to_string(), WOOD.to_string(), BOB);

    let deposit_amount = 1000 * 10u128.pow(18);
    session.sandbox().mint_into(ALICE, 10u128.pow(12)).unwrap();

    session
        .execute(PSP22::transfer(&ice, alice(), deposit_amount, Vec::new()))
        .unwrap()
        .result
        .unwrap()
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/20_
