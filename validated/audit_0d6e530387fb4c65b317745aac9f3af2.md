## Analysis

The external report's core custody invariant is: **a state-mutating pricing/exchange operation that lacks any bound on the acceptable output for the caller lets a third party bracket that operation (front-run + back-run) and redirect value that should have gone to the legitimate participant.** In the Aptos codebase, `object`/`multisig_account`/`resource_account`/`code` all enforce strict single-caller authority checks with no per-call economic bound to exploit (owner checks, k-of-n approvals, `ConstructorRef`/`ExtendRef` capability gating), so they don't reproduce the bug class. The move-examples `bonding_curve_launchpad` module, however, implements exactly this kind of AMM-style value-exchange logic over fungible-asset custody (primary fungible stores holding APT and a bonding-curve FA), and it reproduces the same missing-bound defect.

### Title
Missing slippage/output bound in `liquidity_pairs::swap_apt_to_fa` / `swap_fa_to_apt` enables sandwich theft of swapper funds - (File: `aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move`)

### Summary
The public entry point `bonding_curve_launchpad::swap` [1](#0-0)  forwards directly to `liquidity_pairs::swap_apt_to_fa`/`swap_fa_to_apt`, which compute the exchanged amount purely from the live reserves at execution time via `get_amount_out` [2](#0-1) , with no caller-supplied minimum-output or maximum-input parameter anywhere in the call chain.

### Finding Description
`get_amount_out` only asserts that the computed output is non-zero (`ELIQUIDITY_PAIR_SWAP_AMOUNTOUT_INSIGNIFICANT`), not that it meets any expectation of the caller [3](#0-2) . Both `swap_apt_to_fa` and `swap_fa_to_apt` then move real custody-held assets — APT to/from the swapper's account and FA to/from the swapper's primary fungible store, both via `TransferRef`/`aptos_account::transfer` [4](#0-3) [5](#0-4)  — strictly based on whatever the reserves happen to be at that instant. The entry function `swap` exposes only `amount_in`, never a bound on the resulting output [1](#0-0) .

This is structurally the same custody defect as the reported bug: a value-transfer operation whose executed price depends solely on the *pre-transaction* on-chain state, without any commitment from the initiator about the acceptable output, allows a third party to manipulate that state immediately before and after the victim's transaction (classic sandwich) and capture the resulting price differential — value that should have accrued to the legitimate swapper is diverted to the attacker.

### Impact Explanation
An attacker can steal value directly from any unprivileged user's swap by sandwiching it: front-running with a same-direction trade that worsens the pool price against the victim, letting the victim's `swap` execute at the degraded rate, then back-running to reverse their own trade and capture the victim's lost value. This is a direct theft of custody-held fungible-asset value (APT and the launched FA held in swappers' primary fungible stores and the pool's `FungibleStore`) with no admin/privileged assumption required — any user can attack any other user's pending transaction. Given the constant-product-like curve and lack of any slippage bound, losses scale with trade size and available liquidity depth, making this High severity for any deployment (or fork) of this bonding-curve launchpad pattern.

### Likelihood Explanation
Likelihood is high for any real deployment: this requires only observing the mempool/pending-block for `swap` calls (mempool visibility on Aptos is available to validators/full nodes and can be approximated via block-proposal timing), and issuing two transactions (front-run and back-run) around the victim's transaction — no special privilege, capability, or admin role is needed, unlike the pivots explicitly excluded by the custody gate (governance/admin assumptions, leaked keys, etc.).

### Recommendation
Add a `min_amount_out` (for both swap directions) or equivalently `max_amount_in`, parameter to `swap`, `swap_apt_to_fa`, and `swap_fa_to_apt`, and assert the computed `apt_gained`/`fa_gained` (or `amount_in`) satisfies the caller's bound before executing any transfer, mirroring the standard AMM slippage-protection pattern (as used by, e.g., `swap::router` which this module already depends on). Optionally also support a deadline parameter to bound exposure to delayed inclusion.

### Proof of Concept
1. Liquidity pair has reserves `fa_reserves = F`, `apt_reserves = A`.
2. Victim submits `swap(swap_to_apt = false, amount_in = X)` intending to receive `fa_gained` computed off the current `(F, A)`.
3. Attacker observes the pending victim transaction and front-runs with their own `swap(swap_to_apt = false, amount_in = Y)` (large), which updates reserves to `(F - fa_gained_attacker, A + Y)` per `swap_apt_to_fa` [6](#0-5) .
4. Victim's transaction now executes against the worsened reserves, receiving materially less FA for the same APT paid than originally expected — there is no check preventing this since `swap` never verifies a minimum output.
5. Attacker immediately back-runs with `swap(swap_to_apt = true, amount_in = fa_gained_attacker)` via `swap_fa_to_apt` [7](#0-6) , extracting APT profit sourced from the victim's degraded execution price.

**Caveat**: This finding is located in `aptos-move/move-examples/bonding_curve_launchpad`, a reference/example module rather than the core `aptos-framework`. Its mainnet relevance depends on whether this exact contract (or an unmodified fork) is deployed as-is; I could not verify any live deployment from the repository content alone. If this module is only illustrative and never deployed unmodified, the practical mainnet impact would need to be reassessed on a per-deployment basis.

### Citations

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/bonding_curve_launchpad.move (L164-184)
```text
    public entry fun swap(
        account: &signer,
        name: String,
        symbol: String,
        swap_to_apt: bool,
        amount_in: u64
    ) acquires LaunchPad, FAController {
        // Verify the `amount_in` is valid and that the FA exists.
        assert!(amount_in > 0, ELIQUIDITY_PAIR_SWAP_AMOUNTIN_INVALID);
        // FA Object<Metadata> required for primary_fungible_store interactions.
        // `transfer_ref` is used to bypass the `is_frozen` status of the FA. Without this, the defined dispatchable
        // withdraw function would prevent the ability to transfer the participant's FA onto the liquidity pair.
        let fa_metadata_obj = object::address_to_object(get_fa_obj_address(name, symbol));
        let transfer_ref = &borrow_global<FAController>(get_fa_obj_address(name, symbol)).transfer_ref;
        // Initiate the swap on the associated liquidity pair.
        if (swap_to_apt) {
            liquidity_pairs::swap_fa_to_apt(name, symbol, transfer_ref, account, fa_metadata_obj, amount_in);
        } else {
            liquidity_pairs::swap_apt_to_fa(name, symbol, transfer_ref, account, fa_metadata_obj, amount_in);
        };
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L90-112)
```text
    #[view]
    public fun get_amount_out(
        fa_reserves: u128,
        apt_reserves: u128,
        swap_to_apt: bool,
        amount_in: u64
    ): (u64, u64, u128, u128) {
        if (swap_to_apt) {
            let divisor = fa_reserves + (amount_in as u128);
            let apt_gained = (math128::mul_div(apt_reserves, (amount_in as u128), divisor) as u64);
            let fa_updated_reserves = fa_reserves + (amount_in as u128);
            let apt_updated_reserves = apt_reserves - (apt_gained as u128);
            assert!(apt_gained > 0, ELIQUIDITY_PAIR_SWAP_AMOUNTOUT_INSIGNIFICANT);
            (amount_in, apt_gained, fa_updated_reserves, apt_updated_reserves)
        } else {
            let divisor = apt_reserves + (amount_in as u128);
            let fa_gained = (math128::mul_div(fa_reserves, (amount_in as u128), divisor) as u64);
            let fa_updated_reserves = fa_reserves - (fa_gained as u128);
            let apt_updated_reserves = apt_reserves + (amount_in as u128);
            assert!(fa_gained > 0, ELIQUIDITY_PAIR_SWAP_AMOUNTOUT_INSIGNIFICANT);
            (fa_gained, amount_in, fa_updated_reserves, apt_updated_reserves)
        }
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L212-267)
```text
    public(friend) fun swap_fa_to_apt(
        name: String,
        symbol: String,
        transfer_ref: &TransferRef,
        swapper_account: &signer,
        fa_object_metadata: Object<Metadata>,
        amount_in: u64
    ) acquires Pairs, LiquidityPair {
        // Verify the liquidity pair exists and is enabled for trading.
        assert_liquidity_pair_exists(name, symbol);
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
        // Determine the amount received of APT, when given swapper-supplied amount_in of FA.
        let (fa_given, apt_gained, fa_updated_reserves, apt_updated_reserves) = get_amount_out(
            liquidity_pair.fa_reserves,
            liquidity_pair.apt_reserves,
            true,
            amount_in
        );
        // Verify the swapper holds the FA.
        let swapper_address = signer::address_of(swapper_account);
        let does_primary_store_exist_for_swapper = primary_fungible_store::primary_store_exists(
            swapper_address,
            fa_object_metadata
        );
        assert!(does_primary_store_exist_for_swapper, EFA_PRIMARY_STORE_DOES_NOT_EXIST);
        // Perform the swap.
        // Swapper sends FA to the liquidity pair object. The liquidity pair object sends APT to the swapper, in return.
        let liquidity_pair_signer = object::generate_signer_for_extending(&liquidity_pair.extend_ref);
        let from_swapper_store = primary_fungible_store::ensure_primary_store_exists(
            swapper_address,
            fungible_asset::transfer_ref_metadata(transfer_ref)
        );
        fungible_asset::transfer_with_ref(transfer_ref, from_swapper_store, liquidity_pair.fa_store, fa_given);
        aptos_account::transfer(&liquidity_pair_signer, swapper_address, apt_gained);
        // Record state changes to the liquidity pair's reserves, and emit changes as events.
        let former_fa_reserves = liquidity_pair.fa_reserves;
        let former_apt_reserves = liquidity_pair.apt_reserves;
        liquidity_pair.fa_reserves = fa_updated_reserves;
        liquidity_pair.apt_reserves = apt_updated_reserves;
        event::emit(
            LiquidityPairReservesUpdated {
                former_fa_reserves,
                former_apt_reserves,
                new_fa_reserves: fa_updated_reserves,
                new_apt_reserves: apt_updated_reserves
            }
        );
        event::emit(
            LiquidityPairSwap {
                is_fa_else_apt: false,
                gained: (apt_gained as u128),
                swapper_address
            }
        );
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L270-325)
```text
    public(friend) fun swap_apt_to_fa(
        name: String,
        symbol: String,
        transfer_ref: &TransferRef,
        swapper_account: &signer,
        fa_object_metadata: Object<Metadata>,
        amount_in: u64
    ) acquires Pairs, LiquidityPair {
        // Verify the liquidity pair exists and is enabled for trading.
        assert_liquidity_pair_exists(name, symbol);
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
        // Determine the amount received of FA, when given swapper-supplied amount_in of APT.
        let (fa_gained, apt_given, fa_updated_reserves, apt_updated_reserves) = get_amount_out(
            liquidity_pair.fa_reserves,
            liquidity_pair.apt_reserves,
            false,
            amount_in
        );
        // Perform the swap.
        // Swapper sends APT to the liquidity pair object. The liquidity pair object sends FA to the swapper, in return.
        // Requires the liquidity pair object's address, which is retrieved using the stored extend_ref.
        let swapper_address = signer::address_of(swapper_account);
        let liquidity_pair_address = object::address_from_extend_ref(&liquidity_pair.extend_ref);
        let to_swapper_store = primary_fungible_store::ensure_primary_store_exists(
            swapper_address,
            fungible_asset::transfer_ref_metadata(transfer_ref)
        );
        aptos_account::transfer(swapper_account, liquidity_pair_address, apt_given);
        fungible_asset::transfer_with_ref(transfer_ref, liquidity_pair.fa_store, to_swapper_store, fa_gained);
        // Record state changes to the liquidity pair's reserves, and emit changes as events.
        let former_fa_reserves = liquidity_pair.fa_reserves;
        let former_apt_reserves = liquidity_pair.apt_reserves;
        liquidity_pair.fa_reserves = fa_updated_reserves;
        liquidity_pair.apt_reserves = apt_updated_reserves;
        event::emit(
            LiquidityPairReservesUpdated {
                former_fa_reserves,
                former_apt_reserves,
                new_fa_reserves: fa_updated_reserves,
                new_apt_reserves: apt_updated_reserves
            }
        );
        event::emit(
            LiquidityPairSwap {
                is_fa_else_apt: true,
                gained: (fa_gained as u128),
                swapper_address
            }
        );
        // Check for graduation requirements. The APT reserves must be above the pre-defined
        // threshold to allow for graduation.
        if (liquidity_pair.is_enabled && apt_updated_reserves > APT_LIQUIDITY_THRESHOLD) {
            graduate(liquidity_pair, fa_object_metadata, transfer_ref, apt_updated_reserves, fa_updated_reserves);
        }
    }
```
