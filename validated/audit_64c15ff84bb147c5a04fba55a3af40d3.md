## Custody Analog Found

### Title
Bonding-curve graduation permanently strands ~10% of pooled APT and FA reserves with no recovery path - ([File: aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move])

### Summary
The Aptos-native analog of the Bonding.sol "graduation" flow is `bonding_curve_launchpad`'s `liquidity_pairs::graduate()`, which mirrors the Solidity contract's bonding-curve → external-DEX migration. Unlike the flash-loan report (which concerns *forcing* graduation), the local bug is in what happens *after* graduation: `graduate()` only migrates 90% of the tracked reserves to the new DEX pool, disables the pair forever, and never exposes any way to retrieve the remaining balances. This is a self-contained, code-provable custody bug independent of the external report's exact mechanism, but rooted in the same "atomic graduation with no safety checks" class of bug.

### Finding Description
`swap_apt_to_fa` triggers `graduate()` once `apt_updated_reserves` crosses `APT_LIQUIDITY_THRESHOLD`: [1](#0-0) 

Inside `graduate()`, the pair is permanently disabled and only 90% of both APT and FA reserves are moved to the new external pool: [2](#0-1) 

```
liquidity_pair.is_enabled = false;
...
add_liquidity_coin_entry_transfer_ref<AptosCoin>(
    ...
    ((apt_updated_reserves - (apt_updated_reserves / 10)) as u64),
    ((fa_updated_reserves - (fa_updated_reserves / 10)) as u64),
    0, 0
);
```

Note that `apt_reserves` includes `INITIAL_VIRTUAL_APT_LIQUIDITY` (50_000_000_000 octas) which was never physically deposited: [3](#0-2) [4](#0-3) 

So the pair's real, physical APT balance (held in a `coin::CoinStore<AptosCoin>` at the pair object's address via `aptos_account::transfer`) is `apt_updated_reserves - 50_000_000_000`, which is always **more** than the 90% figure computed by `graduate()` once the threshold (600_000_000_000) is crossed, because `apt_updated_reserves/10 - 50_000_000_000 > 0` for any `apt_updated_reserves > 500_000_000_000`. The un-migrated remainder (real APT never withdrawn, plus real FA never withdrawn from `fa_store`) stays behind.

The pair's `ExtendRef` (needed to generate the pair-object signer that owns both the leftover `fa_store` FungibleStore and the leftover APT `CoinStore`) is stored only inside the `LiquidityPair` resource and is only ever used inside `swap_fa_to_apt`, `swap_apt_to_fa`, and `graduate()`: [5](#0-4) 

Both swap functions require `liquidity_pair.is_enabled == true`: [6](#0-5) [7](#0-6) 

Since `graduate()` sets `is_enabled = false` and there is no other function anywhere in the module that regenerates a signer from `liquidity_pair.extend_ref` or otherwise exposes the pair's `fa_store`/CoinStore, the leftover custody-held value has **no code path back to any account** — not depositors, not the launch creator, not even the module publisher (whose account cannot manufacture the object-generated signer for that address without a module upgrade).

### Impact Explanation
This satisfies the "Permanent lock or non-recoverable loss of object-held ... value" custody-gate criterion:
- Every single graduation permanently strands real, user-deposited APT (worth real money) in an inaccessible `CoinStore` owned by an object whose controlling `ExtendRef`/signer capability is never exposed again.
- It similarly strands ~10%+ of the launched FA's real supply inside a bare `FungibleStore` (`fa_store`) that is not a primary store and has no owner signer path exposed post-graduation.
- This is deterministic and occurs on 100% of graduations, not an edge case — every token that successfully bonds through this launchpad example loses part of its community-contributed liquidity permanently, with no accounting adjustment, refund, or compensating mint.

### Likelihood Explanation
High/deterministic: no attacker or privileged actor is required. Any FA that reaches the graduation threshold under intended, benign usage triggers this loss automatically inside `graduate()`. The loss magnitude scales with the size of the bonding-curve pool at graduation (larger overshoot past `APT_LIQUIDITY_THRESHOLD` → larger stranded amount, since stranded APT ≈ `apt_updated_reserves/10 - 50_000_000_000` plus the FA-side residual and any rounding slack from `router::optimal_liquidity_amounts`).

### Recommendation
In `graduate()`:
1. Compute the amounts to migrate from the pair's **actual physical balances** (`coin::balance<AptosCoin>(pair_address)` and `fungible_asset::balance(fa_store)`), not from a fixed 90%-of-tracked-reserves heuristic that double-counts virtual liquidity.
2. Migrate 100% of the real balances to the new DEX pool (adjusting for whatever ratio `router::add_liquidity_coin` actually consumes), and explicitly sweep any un-consumed remainder (from `optimal_liquidity_amounts` rounding) to a defined recipient (e.g., the FA creator, a treasury, or back into the new pool as a second deposit) rather than leaving it in the now-unreachable pair object.
3. Alternatively, add a dedicated post-graduation rescue/sweep entry function, gated by the pair's stored `ExtendRef`, that any authorized party can call to recover residual `fa_store`/CoinStore balances after `is_enabled` becomes `false`.

### Proof of Concept
1. Launch an FA via `bonding_curve_launchpad::create_fa_pair`.
2. Have swappers call `bonding_curve_launchpad::swap(..., swap_to_apt = false, ...)` (buying FA with APT) repeatedly until `apt_updated_reserves` just exceeds `APT_LIQUIDITY_THRESHOLD` (600_000_000_000 octas), triggering `graduate()` inside `swap_apt_to_fa` ( [1](#0-0) ).
3. After the transaction, read the pair object's raw `coin::balance<AptosCoin>(pair_address)` and the `fa_store`'s `fungible_asset::balance` — both will show a nonzero residual (≈`apt_updated_reserves/10 - 50_000_000_000` octas of real APT, plus any FA-side rounding remainder).
4. Attempt any further `bonding_curve_launchpad::swap` call on the same `name`/`symbol` — it aborts with `ELIQUIDITY_PAIR_DISABLED` ( [7](#0-6) ), and no other public/entry function in the module ever accesses `liquidity_pair.extend_ref` or `liquidity_pair.fa_store` again, confirming the residual value is permanently unreachable.

### Citations

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L19-21)
```text
    const FA_DECIMALS: u8 = 8;
    const INITIAL_VIRTUAL_APT_LIQUIDITY: u128 = 50_000_000_000;
    const APT_LIQUIDITY_THRESHOLD: u128 = 600_000_000_000;
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L68-76)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    struct LiquidityPair has store, key {
        extend_ref: ExtendRef,
        is_enabled: bool,
        is_frozen: bool,
        fa_reserves: u128,
        apt_reserves: u128,
        fa_store: Object<FungibleStore>,
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L187-197)
```text
        move_to(
            &liquidity_pair_signer,
            LiquidityPair {
                extend_ref: liquidity_pair_extend_ref,
                is_enabled: true,
                is_frozen: true,
                fa_reserves: fa_initial_liquidity,
                apt_reserves: INITIAL_VIRTUAL_APT_LIQUIDITY,
                fa_store
            }
        );
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L220-223)
```text
        // Verify the liquidity pair exists and is enabled for trading.
        assert_liquidity_pair_exists(name, symbol);
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L278-281)
```text
        // Verify the liquidity pair exists and is enabled for trading.
        assert_liquidity_pair_exists(name, symbol);
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L320-325)
```text
        // Check for graduation requirements. The APT reserves must be above the pre-defined
        // threshold to allow for graduation.
        if (liquidity_pair.is_enabled && apt_updated_reserves > APT_LIQUIDITY_THRESHOLD) {
            graduate(liquidity_pair, fa_object_metadata, transfer_ref, apt_updated_reserves, fa_updated_reserves);
        }
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L338-356)
```text
    ) {
        // Disable Bonding Curve Launchpad pair and remove global freeze on FA.
        liquidity_pair.is_enabled = false;
        liquidity_pair.is_frozen = false;
        // Offload onto third party, public DEX.
        router::create_pool_coin<AptosCoin>(fa_object_metadata, false);
        let liquidity_pair_signer = object::generate_signer_for_extending(&liquidity_pair.extend_ref);
        add_liquidity_coin_entry_transfer_ref<AptosCoin>(
            transfer_ref,
            &liquidity_pair_signer,
            liquidity_pair.fa_store,
            fa_object_metadata,
            false,
            ((apt_updated_reserves - (apt_updated_reserves / 10)) as u64),
            ((fa_updated_reserves - (fa_updated_reserves / 10)) as u64),
            0,
            0
        );
        // Send liquidity provider tokens to dead address.
```
