# [H] KIN-H02: Malicious users can prevent other users from redeeming rewards by manipulating `total_pooled` with duplicate withdrawal requests

## Summary
Severity: High
Chain: Smart contract
Component: Kintsu
Published: 2024-05-17
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/28
Type: hats-finding

## Details
**Github username:** @coreggon11
**Twitter username:** krikoeth
**Submission hash (on-chain):** 0x1bda75aedd1a99a341c83ebcc4df13c20679af8863a06c9d29b1f32170384788
**Severity:** high

**Description:**
## Description

Users who stake AZERO can withdraw their stakes by first calling `request_unlock` and then, after a certain period they will call `send_batch_unlock_requests` to retrieve the tokens they requested to the vault, along with other requesters in the batch, to call `redeem` afterwards. The [contract checks](https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/blob/29dbb0da84780cc2a6a8ec37d90ee518bc18102c/src/vault/lib.rs#L357) if a `batch_id` was already unlocked, and reverts if it was. However, users can send duplicate `batch_ids` to a single call, resulting in the `total_pooled` being decreased several times by the same amount of requested withdrawals. Since `total_pooled` can be brought to near 0 this way, future calls to `send_batch_unlock_requests` will revert, resulting in users being unable to withdraw, since decreasing of `total_pooled` by a value greater than `total_pooled` will overflow and revert.

## Proof of concept

Consider the following test:

```rust
    #[test]
    fn test_withdraw_all_combined_batches_fail() -> Result<(), Box<dyn Error>> {
        let ctx = setup().unwrap();
        let sess = ctx.sess;

        // Stake 5 million AZERO
        let (_, sess) =
            helpers::call_stake(sess, &ctx.vault, &ctx.share_token, &ctx.alice, 1_000_000).unwrap();
        let (_, sess) =
            helpers::call_stake(sess, &ctx.vault, &ctx.share_token, &ctx.bob, 1_000_000).unwrap();
        let (_, sess) =
            helpers::call_stake(sess, &ctx.vault, &ctx.share_token, &ctx.charlie, 1_000_000)
                .unwrap();
        let (_, sess) =
            helpers::call_stake(sess, &ctx.vault, &ctx.share_token, &ctx.dave, 1_000_000).unwrap();
        let (_, sess) =
            helpers::call_stake(sess, &ctx.vault, &ctx.share_token, &ctx.ed, 1_000_000).unwrap();

        let (first_batch_id, sess) = helpers::query_batch_id(sess, &ctx.vault).unwrap();

        // Request unlocking of 0.5 million AZERO
        let (_, sess) =
            helpers::call_request_unlock(sess, &ctx.vault, &ctx.share_token, &ctx.alice, 500_000)
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/28_
