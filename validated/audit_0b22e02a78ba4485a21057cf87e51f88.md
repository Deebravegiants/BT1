Confirmed: there is no public/entry function anywhere in `bonding_curve_launchpad` or `liquidity_pairs` that lets anyone withdraw the residual reserves left in a `LiquidityPair` object after `graduate()` runs. Only `create_fa_pair`, `swap`, and view functions are exposed; `graduate` is a private `fun` called only from inside `swap_apt_to_fa`.

### Title
Post-graduation residual APT/FA reserves permanently stranded in `LiquidityPair` object with no withdrawal path - (File: aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move)

### Summary
When a bonding-curve pair "graduates" to the external `swap` DEX, `graduate()` moves only 90% of the pair's tracked reserves into the new DEX pool and leaves the object disabled (`is_enabled = false`) forever. There is no function in `liquidity_pairs.move` or `bonding_curve_launchpad.move` that can extract the leftover APT/FA (or the destination is not `@0xdead`) after this point, so the residual value is permanently locked, mirroring the `BatonLaunchpad` "fees stuck with no withdraw method" pattern.

### Finding Description
`graduate()` computes 90% of the current reserves to seed the external liquidity pool and intentionally discards the remaining 10%: [1](#0-0) 

Specifically: [2](#0-1) 

After this call, `liquidity_pair.is_enabled` is `false` and `is_frozen` is `false` [3](#0-2) 

Every subsequent swap call requires `liquidity_pair.is_enabled` to be true (`swap_fa_to_apt`/`swap_apt_to_fa` both assert this): [4](#0-3) [5](#0-4) 

So once `is_enabled` flips to `false` at graduation, the `LiquidityPair` object (its `apt_reserves` field and its `fa_store` FungibleStore) can never be touched again through this module's public entry points. The object's `ExtendRef` is held only inside the `LiquidityPair` struct itself and never exposed to any caller-facing function outside of the swap/graduate flow, and there is no `withdraw`/`sweep`/`admin_withdraw`/`skim` entry function anywhere in `bonding_curve_launchpad.move` or `liquidity_pairs.move` (confirmed via full read of both files — the only `public`/`public entry` functions are `create_fa_pair`, `swap`, and the view functions `get_amount_out`, `get_is_frozen_metadata`, `get_pair_obj_address`, `get_fa_obj_address`, `get_balance`, `get_metadata`, `get_is_frozen`).

Note: the pre-graduation `apt_reserves` also includes `INITIAL_VIRTUAL_APT_LIQUIDITY` (virtual, non-real APT), so the 10% retained-in-object figure computed from `apt_updated_reserves` is an overstatement relative to actual on-chain balance held by the object; still, whatever real APT and FA remain physically in the `LiquidityPair` object's account/`fa_store` post-graduation are unreachable by design.

### Impact Explanation
This is a permanent, non-recoverable loss of custody: real APT and real FA tokens that swappers deposited into the pair remain physically held at the `LiquidityPair` object address (and its `fa_store` sub-object) with no code path — no owner/admin function, no `ExtendRef` exposure, no `TransferRef`-based sweep — capable of moving them out once `is_enabled` is set to `false`. This satisfies "Permanent lock or non-recoverable loss of object-held … value" under the custody impact gate. Because graduation is a normal, expected, and likely-to-occur event (it is the intended end state of every successful bonding-curve launch), the affected value (10% of both FA and real APT reserves per graduated pair) is lost for every single pair that reaches the liquidity threshold.

### Likelihood Explanation
High. Graduation is not an edge case — it is the designed terminal state of the bonding curve mechanic, triggered automatically whenever `apt_updated_reserves > APT_LIQUIDITY_THRESHOLD` during a normal `swap_apt_to_fa` call: [6](#0-5) 
Every FA pair that becomes popular enough to reach the threshold will trigger this stranding of funds automatically and unavoidably, with no user or admin action needed to cause it, and no way to prevent or reverse it afterward.

### Recommendation
Add a permissioned (or even permissionless, sending to a defined treasury/burn address) sweep function in `liquidity_pairs.move`, callable only after `is_enabled == false`, that uses the stored `extend_ref` to generate the `LiquidityPair` object's signer, withdraws the remaining `fa_store` balance via `fungible_asset::withdraw` and the remaining native APT balance via `coin::withdraw`, and transfers both to a designated recipient (e.g., the original creator, a DAO treasury, or split among LPs). Alternatively, change `graduate()` to seed the external pool with 100% of real reserves (accounting properly for virtual liquidity) so nothing is left behind.

### Proof of Concept
1. Call `create_fa_pair` to launch a new FA/APT pair via `bonding_curve_launchpad::create_fa_pair`.
2. Repeatedly call `bonding_curve_launchpad::swap(account, name, symbol, false, amount_in)` (APT → FA) until `apt_updated_reserves > APT_LIQUIDITY_THRESHOLD` (600_000_000_000), triggering the internal call to `graduate()` inside `swap_apt_to_fa` (`liquidity_pairs.move:322-324`).
3. Observe that `graduate()` moves only `apt_updated_reserves - apt_updated_reserves/10` and `fa_updated_reserves - fa_updated_reserves/10` into the new DEX pool (`liquidity_pairs.move:351-352`), leaving ~10% of both assets physically in the `LiquidityPair` object/`fa_store`.
4. Confirm `liquidity_pair.is_enabled` is now `false` (`liquidity_pairs.move:340`), so both `swap_fa_to_apt` and `swap_apt_to_fa` will abort with `ELIQUIDITY_PAIR_DISABLED` for that pair going forward (`liquidity_pairs.move:222-223`, `280-281`).
5. Attempt to locate any function capable of extracting the remaining balance from the `LiquidityPair` object or its `fa_store` — none exists in `bonding_curve_launchpad.move` or `liquidity_pairs.move`; the residual assets are permanently unrecoverable.

### Citations

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

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L332-373)
```text
    fun graduate(
        liquidity_pair: &mut LiquidityPair,
        fa_object_metadata: Object<Metadata>,
        transfer_ref: &TransferRef,
        apt_updated_reserves: u128,
        fa_updated_reserves: u128
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
        let apt_coin_wrapped = coin_wrapper::get_wrapper<AptosCoin>();
        let liquidity_obj = liquidity_pool::liquidity_pool(apt_coin_wrapped, fa_object_metadata, false);
        let liquidity_pair_address = signer::address_of(&liquidity_pair_signer);
        liquidity_pool::transfer(
            &liquidity_pair_signer,
            liquidity_obj,
            @0xdead,
            primary_fungible_store::balance(liquidity_pair_address, liquidity_obj)
        );
        // Emit event informing all that the liquidity pair has graduated and which DEX it graduated to.
        event::emit(
            LiquidityPairGraduated {
                fa_object_metadata,
                dex_address: @swap
            }
        );
    }
```
