### Title
Duplicate liquidation debt legs can burn the same debt position twice - ([File: contracts/controller/src/positions/liquidation/apply.rs](contracts/controller/src/positions/liquidation/apply.rs))

### Summary
`liquidate` accepts a user-supplied `debt_payments` vector, and the repayment application path builds one pool action per planned leg. If the same debt market appears more than once, each action embeds the same pre-repayment `DebtPosition` because the account book is not merged until after the batch returns. This mirrors the SFQ defect class: the liquidation plan’s aggregate payment list can represent more work than the still-current account position contains.

The available evidence shows the vulnerable shape, but I could not fully verify whether upstream liquidation planning deduplicates `debt_payments` before constructing `repaid`. If it does not, this can corrupt pool/account accounting or make liquidation unusable for affected accounts.

### Finding Description
In `apply_liquidation_repayments`, each `RepayEntry` is converted directly into a `PoolAction`. For every entry, the controller reads `account.borrow_positions[entry.hub_asset]` and places that current scaled debt into the action. The position is updated only later, inside `apply_repay_batch`, after the whole batch has been submitted to the pool.

For duplicate market entries, the sequence is:

1. First leg reads debt position `D` and submits `PoolAction { position: D, amount: x }`.
2. Second leg again reads the unchanged debt position `D` and submits `PoolAction { position: D, amount: y }`.
3. Pool execution can therefore apply both legs against the same starting position rather than against `D - x` for the second leg.
4. Controller merging then processes each returned mutation independently.

This is analogous to `sch->q.len` being inflated by packets in `gso_skb`: the operation count says there are multiple independently payable legs, while the account’s actual queue of debt position state contains only the original position once.

### Impact Explanation
Depending on the pool’s per-entry semantics, the second duplicate leg can either:

- revert on an insufficient-position subtraction, leaving the account unliquidatable through the affected payment shape;
- over-burn debt if the pool treats each supplied position independently;
- or produce inconsistent controller and pool books, threatening the account/pool reconciliation invariant.

The strongest reachable impact is permanent or repeated freezing of liquidation for an unhealthy account if duplicate planned legs always revert. If the pool instead applies the stale positions successfully, the impact can become theft of user funds or protocol insolvency through debt being removed without corresponding measured repayment.

### Likelihood Explanation
The entrypoint is callable by any liquidator for an eligible unhealthy account, so no privileged role is needed. Likelihood depends on whether liquidation planning accepts duplicate `debt_payments` markets or emits duplicate `RepayEntry` values. I could not verify that final planning stage in the available iteration. If duplicates reach `apply_liquidation_repayments`, the condition is deterministic because every leg snapshots the same unchanged `borrow_positions` entry before `apply_repay_batch`.

### Recommendation
Aggregate `debt_payments` and planned `RepayEntry` values by `HubAssetKey` before constructing `PoolAction`s, or carry a running position through the loop and make each subsequent leg consume the prior leg’s result. Also add a regression test where `liquidate` receives duplicate debt-market payments and assert one consolidated pool action is submitted.

### Proof of Concept
Conceptual call:

```text
liquidate(
    liquidator = attacker,
    account_id = victim_undercollateralized_account,
    debt_payments = [
        (debt_asset, amount_x),
        (debt_asset, amount_y)
    ],
    seize_mode = Transfer
)
```

Both `RepayEntry` legs for `debt_asset` enter `apply_liquidation_repayments`. The first action embeds the victim’s unchanged debt position; the second embeds that same unchanged position again before `apply_repay_batch` merges any result. The duplicate legs therefore operate on stale position state rather than on a queue whose tail has been cleared by the first repayment.