### Title
Fee-free `flash_position` replicates fee-charged `multiply`, letting users open identical leveraged positions without paying the origination fee - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
The protocol charges a flash-style origination fee on strategy debt opened through `multiply` and `swap_debt` (`charge_fee = true`), but mints the identical class of strategy debt fee-free through `flash_position` (`charge_fee = false`). Both paths converge on the same `strategy_finalize` risk checks and produce the same end state — new debt plus newly deposited measured collateral on one account. An unprivileged user can therefore achieve the same leveraged outcome through `flash_position` with their own receiver contract and pay zero fee, draining protocol revenue relative to the `multiply` path.

### Finding Description
The pool's strategy op withholds `flashloan_fee` bps of principal as protocol revenue only when `charge_fee` is set:

`contracts/pool/src/ops/strategy.rs:94-101`
```rust
fn compute_fee(env: &Env, cache: &Cache, amount: i128, charge_fee: bool) -> i128 {
    if !charge_fee {
        return 0;
    }
    let fee = Bps::from(i128::from(cache.params().flashloan_fee)).flash_loan_fee_on(env, amount);
    ...
}
```

`multiply` passes `charge_fee = true`; `flash_position` mints the same debt via `borrow_into_controller(..., false, PositionAction::FlashPos, ...)` — the `false` is the `charge_fee` flag — then forwards the full proceeds to a caller-supplied WASM receiver:

`contracts/controller/src/strategies/flash_position.rs:271-294` (`mint_and_forward`)

The receiver only has to push back measured collateral meeting the caller-declared `collaterals` minimums and pass the same finalization/HF checks as `multiply`. The receiver can implement any route (own funds, own swaps on Aquarius/Soroswap) since it is just the user's own contract; unlike `multiply`, it is not even restricted to the configured router — the router is the only difference, and it is what the fee is nominally paying for, yet the fee-free path offers strictly more flexibility.

The codebase's own parity test proves the asymmetry end-to-end: `tests/test-harness/tests/strategy_origination_fee_parity.rs:97-129` opens the same 1.0 ETH leverage via both routes and asserts `multiply` books exactly `flashloan_fee` bps of revenue while `flash_position` books zero and ends with *more* collateral for the same debt.

Impact is asymmetric the same way as the source report: whenever `flashloan_fee > 0`, every leveraged-position user is economically better off routing through `flash_position` (or mixing, e.g., a `multiply`-equivalent swap inside their own receiver), so the origination fee is effectively optional and treasury revenue is under-collected. The divergence grows linearly with position size (up to `MAX_FLASHLOAN_FEE_BPS = 500` bps).

### Impact Explanation
Protocol revenue loss on every leveraged position opened via `flash_position` instead of `multiply`/`swap_debt`: up to 5% of principal per position that would otherwise have been withheld as fee. Users additionally receive strictly more collateral for identical debt, so rational flow migrates to the fee-free path, making `multiply`'s fee structurally uncollectable.

### Likelihood Explanation
Reachable by any unprivileged address: `flash_position` requires only `require_auth`, a flashloanable debt asset, and a WASM receiver the caller controls (explicitly allowed — only the controller and pool addresses are rejected). No privileged config, no external precondition beyond a configured `flashloan_fee > 0`. The only friction is deploying a receiver contract, which is permissionless on Soroban and reusable across all positions and users.

### Recommendation
Charge the origination fee symmetrically. Either pass `charge_fee = true` in `mint_and_forward` (withholding the fee before forwarding to the receiver), or — mirroring the source report's mitigation — charge the fee on a quantity that cannot be dodged by path selection, e.g., apply the fee at debt-mint time on `action.amount` regardless of which strategy entrypoint created the debt, so `multiply`, `swap_debt`, and `flash_position` all pay the same rate for the same debt.

### Proof of Concept
The repository already contains the executable PoC at `tests/test-harness/tests/strategy_origination_fee_parity.rs`:

1. `open_via_multiply()` calls `multiply(ALICE, "USDC", 1.0, "ETH", PositionMode::Multiply, steps)`; pool revenue in ETH increases by exactly `flashloan_fee` bps of the 1.0 ETH principal (`expected_fee = 10_000_000 - apply_flash_fee(10_000_000)`).
2. `open_via_flash_position()` calls `flash_position` with a deployed receiver that returns 3,000 USDC collateral; the account ends with the same ~1.0 ETH debt and **more** USDC collateral, while `revenue_after - revenue_before == 0`.

The test asserts `fp_collateral > mul_collateral` and `fp_revenue == 0` — the same leveraged outcome for strictly less fee, reachable today by any user pointing `flash_position` at their own receiver contract.