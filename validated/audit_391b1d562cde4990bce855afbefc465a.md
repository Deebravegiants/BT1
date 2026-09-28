### Title
Attacker can pin utilization at `max_utilization` to freeze all supplier withdrawals - ([File: contracts/pool/src/guards.rs])

### Summary
`require_utilization_below_max` is an absolute post-state guard applied to every non-liquidation withdrawal. Because burning supply shares lowers the denominator, any withdrawal from a market sitting at or above `max_utilization` reverts. A single unprivileged borrower can drive utilization to the cap with ordinary borrows and keep it pinned, making every supplier withdrawal fail with `UtilizationAboveMax` for as long as the position is maintained.

### Finding Description
In `contracts/pool/src/ops/withdraw.rs`, `gate_and_debit` runs `guards::require_utilization_below_max` after shares are burned, unless the withdrawal is a liquidation or a footprint-only close.

`contracts/pool/src/guards.rs:19-34` computes utilization as `borrowed_ceil / supplied_floor` and panics when it exceeds `params.max_utilization`. Because the check runs post-burn, a withdrawal strictly raises utilization: `(B)/(S−x) > B/S`. At `max_utilization = 1.0` this is the standard "100% utilization blocks withdrawals" property, but here it applies at whatever cap is configured, and the cap is checked against ceiled debt value and floored supply value — rounding pushes utilization upward.

An attacker reaches this state through the permissionless `controller::borrow` path (which itself only requires post-borrow utilization ≤ `max_utilization`, plus the 2% `LIQUIDATION_BUFFER_BPS` cash reserve in `require_liquidation_buffer`). Borrowing exactly to the cap is admissible; from that point every supplier's `withdraw` reverts until the attacker repays or liquidations consume the debt. Accruing interest alone keeps utilization at or above the cap over time, so the attacker only needs periodic re-borrows to maintain the pin. `claim_revenue` is also gated by `require_utilization_below_max` (per the pool README guard table), so unclaimed protocol yield is frozen at the same time.

The docs acknowledge the mechanics ("burning supply shares raises utilization, so once utilization reaches the cap no withdrawal of any size passes... It is released by repayment, or consumed by liquidation"), but they treat it as a state property, not as an attacker-reachable griefing vector: a rational borrower can hold the cap deliberately rather than arriving there organically.

### Impact Explanation
Temporary freezing of funds: all suppliers in the pinned market are unable to withdraw any amount while utilization sits at or above the cap, and protocol revenue cannot be claimed. The freeze is not self-limiting — the attacker's accrued debt keeps utilization high, and only the attacker's repayment or a liquidation (which requires the attacker to become undercollateralized, i.e., a price move) releases it. Funds are eventually recoverable, so the impact is temporary, not permanent, freezing.

### Likelihood Explanation
Medium. The attack requires real collateral: `borrow` enforces the caller's health factor and `min_borrow_collateral_usd`, so the attacker must fund a separate collateral position, and pays borrow interest for the duration. The freeze also ends if prices move enough to liquidate the attacker. No privileged role, leaked key, or off-chain component is involved — a single unprivileged account with sufficient collateral can initiate and sustain it.

### Recommendation
- Apply the utilization check pre-withdrawal (or compare utilization before and after and only reject if the withdrawal itself worsened a below-cap market), so exits at the cap remain possible.
- Alternatively, exempt withdrawals up to the amount that keeps post-state utilization at or below the pre-withdrawal utilization, preserving the cap for entry while decoupling exit availability from an adversarial borrow.

### Proof of Concept
1. Supplier S calls `controller::supply` into market M; other liquidity exists.
2. Attacker A supplies collateral in a second market and calls `controller::borrow` on market M repeatedly until `borrowed.div_ceil(supplied) == max_utilization` (allowed: `require_utilization_below_max` admits equality, `require_liquidation_buffer` only reserves the last 2% of cash).
3. S calls `controller::withdraw` for any positive amount. In `withdraw::accounting` → `gate_and_debit`, burning S's shares lowers `supplied`, so `borrowed.div_ceil(supplied')` exceeds `max_utilization` → panic `UtilizationAboveMax` (127).
4. A re-borrows or relies on interest accrual to keep utilization pinned; every subsequent `withdraw` and `claim_revenue` reverts until A repays.