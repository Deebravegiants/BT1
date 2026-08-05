### Title
Donation-based reserve inflation allows an attacker to steal a victim's `add_liquidity` deposit in `pallet-asset-conversion` - (File: substrate/frame/asset-conversion/src/lib.rs)

### Summary
`Pallet::do_add_liquidity` prices liquidity contributions using `Self::get_balance`, which returns the *actual* token balance of the pool account (`T::PoolLocator::address`) rather than an internally-tracked reserve that only updates through `add_liquidity`/`swap` calls. Because any unprivileged account can transfer tokens directly into the pool account (e.g. via `Balances::transfer`/`Assets::transfer`), an attacker can donate tokens to skew the pool ratio and/or dilute the LP-share price before a victim's `add_liquidity` call, causing the victim's real deposit to mint disproportionately few LP tokens while the attacker's existing/near-simultaneous LP position captures a share of the inflated pool.

### Finding Description
`create_pool` initializes a pool with zero total LP supply and an empty pool account. `Self::get_balance(&pool_account, asset_id)` (used to derive `reserve1`/`reserve2` in `do_add_liquidity`, `do_swap`, and `do_remove_liquidity`) is a direct read of the account's fungible/asset balance rather than a value only mutated by pallet-controlled deposit/withdraw logic. This is the classic "balance-as-reserve" pattern that is vulnerable to the well-known first-depositor/donation (vault share-inflation) attack seen in Uniswap V2 forks and ERC4626 vaults:

1. Attacker calls `create_pool(asset1, asset2)`.
2. Attacker becomes (or ensures they remain) the first real LP by calling `add_liquidity` with a minimal amount, so `total_supply.is_zero()` branch mints LP based on `calc_lp_amount_for_zero_supply(amount1, amount2)`, subtracting the fixed `T::MintMinLiquidity` burn.
3. Attacker separately/immediately transfers ("donates") a large, skewed amount of `asset1`/`asset2` directly into the pool account, inflating `reserve1`/`reserve2` as read by `get_balance`, without minting any additional LP tokens for that donation.
4. Victim calls `add_liquidity`. Since `total_supply` is now non-zero, the pallet takes the proportional-mint branch: `lp_minted = min(amount1 * total_supply / reserve1, amount2 * total_supply / reserve2)`. Because `reserve1`/`reserve2` are inflated by the donation while `total_supply` remains small (only the attacker's tiny initial mint plus the locked `MintMinLiquidity`), the victim's large deposit yields a disproportionately small (or, due to integer division, near-zero) amount of minted LP tokens.
5. Attacker calls `remove_liquidity`, redeeming their LP share against the now-inflated reserve (which includes both their own donation and the victim's freshly added tokens), extracting value far exceeding their own contribution.

`MintMinLiquidity` (the Uniswap V2-style `MINIMUM_LIQUIDITY` burn) only bounds the *initial* mint size and permanently locks a fixed amount of LP supply; it does not protect against externally-donated token balances inflating `reserve1`/`reserve2` independent of LP accounting, because donations bypass `add_liquidity`/mint logic entirely. The check only affects the very first mint calculation (based on the caller's own declared `amount1_desired`/`amount2_desired`, not the pool's actual balance), so it does not defend subsequent depositors (like the victim) once `total_supply` is non-zero and reserves have been externally skewed.

### Impact Explanation
A victim's `add_liquidity` deposit can be diluted such that they receive far fewer LP tokens than their contribution warrants, while the attacker's existing LP position (inflated in value by the same donation) can be redeemed via `remove_liquidity` to extract a disproportionate share of the pool — effectively transferring value from the victim to the attacker. This matches the scoped "pool drain" impact.

### Likelihood Explanation
This requires only unprivileged actions available to any signed account: `create_pool` (permissionless), ordinary asset/balance transfers to the deterministic, publicly-known `T::PoolLocator::address` for a given pool, and a normal `add_liquidity`/`remove_liquidity` call. The main constraint is the attacker's capital to fund the donation and the fixed cost of the permanently-burned `MintMinLiquidity` amount; for sufficiently large victim deposits, this cost is negligible relative to extractable value. The attack is repeatable against any newly created pool the attacker can front-run before it accumulates significant real liquidity.

### Recommendation
Do not derive `reserve1`/`reserve2` from raw account balance via `get_balance`. Track pool reserves internally in dedicated storage that is only mutated by `do_add_liquidity`, `do_remove_liquidity`, and `do_swap`, and reconcile/ignore any balance surplus (or sweep unexpected surplus to protocol fees rather than reserve-ratio pricing) so directly-transferred tokens cannot influence LP minting or swap pricing. Additionally, consider requiring a minimum LP-token-out check (slippage protection with `mint_amount > 0` and above a meaningful threshold) so victims can set safe minimums.

### Proof of Concept
Fuzz/integration test plan for `substrate/frame/asset-conversion/src/tests.rs`:
1. `create_pool(asset1, asset2)`.
2. Attacker calls `add_liquidity` with minimal amounts to become first LP (records attacker's LP token balance and cost).
3. Attacker transfers a large skewed amount of `asset1`/`asset2` directly to the pool account (bypassing `add_liquidity`).
4. Victim calls `add_liquidity` with a realistic, fairly-priced amount; record victim's minted LP tokens and tokens actually transferred in.
5. Attacker calls `remove_liquidity` for their full LP balance; record tokens received.
6. Assert conservation-of-value invariant: victim's `(LP tokens minted / total supply) * pool value` should be >= victim's real contribution value minus fees; assert this fails (attacker's extracted value > attacker's own contribution + fees), demonstrating the vulnerability.