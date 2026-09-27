import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 10
# todo: the path from https://github.com/XOXNO/rs-lending-xlm
SOURCE_REPO = "XOXNO/rs-lending-xlm"
# todo: the name of the repository
REPO_NAME = "rs-lending-xlm"
run_number = os.environ.get('GITHUB_RUN_NUMBER') or os.environ.get('CI_PIPELINE_IID', '0')


def get_cyclic_index(run_number, max_index=100):
    """Convert run number to a cyclic index between 1 and max_index"""
    return (int(run_number) - 1) % max_index + 1


def load_repository_urls():
    """Load repository URLs from repositories.json."""
    repo_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repositories.json")
    if not os.path.exists(repo_file):
        return []

    try:
        with open(repo_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return [url for url in data if isinstance(url, str) and url.strip()]


if run_number == "0":
    BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"
else:
    repository_urls = load_repository_urls()
    if repository_urls:
        run_index = get_cyclic_index(run_number, len(repository_urls))
        BASE_URL = repository_urls[run_index - 1]
    else:
        BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"


scope_files = [
    # =================================================================================
    # Controller entry points: every #[contractimpl] user, keeper and admin endpoint,
    # read-only views, and the governance-facing admin surface
    # =================================================================================
    "contracts/controller/src/lib.rs",
    "contracts/controller/src/views.rs",
    "contracts/controller/src/governance.rs",
    "contracts/controller/src/markets.rs",
    "contracts/controller/src/constants.rs",

    # =================================================================================
    # Account authority: NFT-owned accounts, owner/delegate checks, spoke binding,
    # account creation, position upsert/removal and account deletion with NFT burn
    # =================================================================================
    "contracts/controller/src/account.rs",
    "contracts/controller/src/storage/account.rs",
    "contracts/controller/src/storage/hub.rs",
    "contracts/controller/src/storage/mod.rs",
    "contracts/controller/src/storage/protocol.rs",
    "contracts/controller/src/storage/spoke.rs",

    # =================================================================================
    # Operation context: cached market indexes, prices and spoke listings per call
    # =================================================================================
    "contracts/controller/src/context.rs",
    "contracts/controller/src/payments.rs",
    "contracts/controller/src/spoke_usage.rs",

    # =================================================================================
    # Position flows: supply, withdraw, borrow, repay, entry gates, listing flags,
    # post-pool solvency enforcement
    # =================================================================================
    "contracts/controller/src/positions/mod.rs",
    "contracts/controller/src/positions/supply.rs",
    "contracts/controller/src/positions/debt.rs",

    # =================================================================================
    # Liquidation and bad debt: plan, bonus curve, pro-rata seizure, whole-unit legs,
    # Transfer/Credit settlement, cleanup and socialization
    # =================================================================================
    "contracts/controller/src/positions/liquidation/mod.rs",
    "contracts/controller/src/positions/liquidation/plan.rs",
    "contracts/controller/src/positions/liquidation/math.rs",
    "contracts/controller/src/positions/liquidation/curve.rs",
    "contracts/controller/src/positions/liquidation/apply.rs",
    "contracts/controller/src/positions/liquidation/bad_debt.rs",

    # =================================================================================
    # Account risk: USD totals, health factor, cached risk params, threshold restamps,
    # flash guard, position limits, whole-unit collateral gates
    # =================================================================================
    "contracts/controller/src/risk/mod.rs",
    "contracts/controller/src/risk/params.rs",
    "contracts/controller/src/risk/totals.rs",
    "contracts/controller/src/risk/validation.rs",

    # =================================================================================
    # Strategies: cash flash loan, flash position callback, multiply, swap debt/collateral,
    # repay with collateral, router swap measurement, Blend migration
    # =================================================================================
    "contracts/controller/src/strategies/mod.rs",
    "contracts/controller/src/strategies/flash_loan.rs",
    "contracts/controller/src/strategies/flash_position.rs",
    "contracts/controller/src/strategies/multiply.rs",
    "contracts/controller/src/strategies/swap.rs",
    "contracts/controller/src/strategies/swap_debt.rs",
    "contracts/controller/src/strategies/swap_collateral.rs",
    "contracts/controller/src/strategies/repay_debt_with_collateral.rs",
    "contracts/controller/src/strategies/legs.rs",
    "contracts/controller/src/strategies/migrate_blend.rs",

    # =================================================================================
    # Listing and spoke configuration consumed by every risk check
    # =================================================================================
    "contracts/controller/src/config/mod.rs",
    "contracts/controller/src/config/asset.rs",
    "contracts/controller/src/config/registry.rs",
    "contracts/controller/src/config/spoke.rs",

    # =================================================================================
    # Cross-contract calls from the controller: pool, position NFT, price aggregator, Blend
    # =================================================================================
    "contracts/controller/src/external/mod.rs",
    "contracts/controller/src/external/pool.rs",
    "contracts/controller/src/external/position_nft.rs",
    "contracts/controller/src/external/price_aggregator.rs",
    "contracts/controller/src/external/blend.rs",

    # =================================================================================
    # Controller events (gross/net amounts that integrators and keepers trust)
    # =================================================================================
    "contracts/controller/src/events/mod.rs",
    "contracts/controller/src/events/config.rs",
    "contracts/controller/src/events/market.rs",

    # =================================================================================
    # Pool: custody, cash book, share/index scaling, market batching, guards, accrual
    # =================================================================================
    "contracts/pool/src/lib.rs",
    "contracts/pool/src/storage.rs",
    "contracts/pool/src/guards.rs",
    "contracts/pool/src/interest.rs",
    "contracts/pool/src/time.rs",
    "contracts/pool/src/views.rs",
    "contracts/pool/src/events.rs",
    "contracts/pool/src/cache/mod.rs",
    "contracts/pool/src/cache/cash.rs",
    "contracts/pool/src/cache/scale.rs",
    "contracts/pool/src/cache/shares.rs",
    "contracts/pool/src/cache/report.rs",

    # =================================================================================
    # Pool operations: supply, borrow, withdraw, repay, net settle, seize, flash,
    # strategy debt minting, recapitalize, revenue claim, market lifecycle
    # =================================================================================
    "contracts/pool/src/ops/mod.rs",
    "contracts/pool/src/ops/supply.rs",
    "contracts/pool/src/ops/borrow.rs",
    "contracts/pool/src/ops/withdraw.rs",
    "contracts/pool/src/ops/repay.rs",
    "contracts/pool/src/ops/net_settle.rs",
    "contracts/pool/src/ops/seize.rs",
    "contracts/pool/src/ops/flash.rs",
    "contracts/pool/src/ops/strategy.rs",
    "contracts/pool/src/ops/recapitalize.rs",
    "contracts/pool/src/ops/revenue.rs",
    "contracts/pool/src/ops/market.rs",

    # =================================================================================
    # Price aggregator: source resolution, dual-leg tolerance, sanity bands, session
    # cache, Reflector / RedStone-format / Aquarius LP providers, admission checks
    # =================================================================================
    "contracts/price-aggregator/src/lib.rs",
    "contracts/price-aggregator/src/engine.rs",
    "contracts/price-aggregator/src/session.rs",
    "contracts/price-aggregator/src/tolerance.rs",
    "contracts/price-aggregator/src/validation.rs",
    "contracts/price-aggregator/src/observation.rs",
    "contracts/price-aggregator/src/properties.rs",
    "contracts/price-aggregator/src/registry.rs",
    "contracts/price-aggregator/src/admin.rs",
    "contracts/price-aggregator/src/providers/aquarius.rs",
    "contracts/price-aggregator/src/providers/multi_feed.rs",
    "contracts/price-aggregator/src/providers/reflector.rs",

    # =================================================================================
    # Governance: typed operations, timelock lifecycle and permissionless execute,
    # immediate roles, recovery, proposal-time validation, deployment helpers
    # =================================================================================
    "contracts/governance/src/lib.rs",
    "contracts/governance/src/api.rs",
    "contracts/governance/src/access.rs",
    "contracts/governance/src/op.rs",
    "contracts/governance/src/storage.rs",
    "contracts/governance/src/deploy.rs",
    "contracts/governance/src/events.rs",
    "contracts/governance/src/constants.rs",
    "contracts/governance/src/timelock/mod.rs",
    "contracts/governance/src/timelock/lifecycle.rs",
    "contracts/governance/src/timelock/immediate.rs",
    "contracts/governance/src/timelock/recovery.rs",
    "contracts/governance/src/validate/mod.rs",
    "contracts/governance/src/validate/asset.rs",
    "contracts/governance/src/validate/tolerance.rs",

    # =================================================================================
    # Position NFT: account ownership, transfer/approve, controller-gated mint/burn, renew
    # =================================================================================
    "contracts/position-nft/src/contract.rs",

    # =================================================================================
    # Shared math and rates: WAD/RAY fixed point, rounding, rate curve, compounding,
    # index growth, share scaling, accrual simulation
    # =================================================================================
    "common/src/math/fp_core.rs",
    "common/src/math/fp.rs",
    "common/src/rates/mod.rs",
    "common/src/rates/curve.rs",
    "common/src/rates/compound.rs",
    "common/src/rates/index.rs",
    "common/src/rates/scaling.rs",
    "common/src/rates/simulate.rs",
    "common/src/rates/value.rs",

    # =================================================================================
    # Shared oracle logic: LP fair pricing (constant product and stable), observation
    # scaling and timestamps, provider clients
    # =================================================================================
    "common/src/oracle/lp.rs",
    "common/src/oracle/lp_stable.rs",
    "common/src/oracle/observation.rs",
    "common/src/oracle/providers/aquarius.rs",
    "common/src/oracle/providers/redstone.rs",
    "common/src/oracle/providers/reflector.rs",
    "common/src/oracle/providers/xoxno.rs",

    # =================================================================================
    # Shared types, constants, token transfer measurement, validation, TTL, errors
    # =================================================================================
    "common/src/types/controller.rs",
    "common/src/types/pool.rs",
    "common/src/types/oracle.rs",
    "common/src/types/composable_oracle.rs",
    "common/src/types/shared.rs",
    "common/src/constants/shared.rs",
    "common/src/constants/pool.rs",
    "common/src/token.rs",
    "common/src/validation.rs",
    "common/src/collections.rs",
    "common/src/ttl.rs",
    "common/src/errors.rs",

    # =================================================================================
    # Public contract interfaces for the in-scope contracts
    # =================================================================================
    "interfaces/controller/src/lib.rs",
    "interfaces/controller/src/admin.rs",
    "interfaces/pool/src/lib.rs",
    "interfaces/governance/src/lib.rs",
    "interfaces/position-nft/src/lib.rs",
    "interfaces/price-aggregator/src/lib.rs",
]


target_scopes = [
    "Critical. A liquidator seizes more collateral than the debt it actually retires plus the capped bonus, or retires debt it never paid: build_liquidation_plan, calculate_repayment_amounts, normalize_repayment_plan, whole_unit_repayment, calculate_seizure_proportions, calculate_seized_collateral, split_seized_shares, scale_seizures_to_received, release_unbacked_repayment, process_excess_payment and apply_liquidation_repayments / apply_liquidation_seizures / apply_liquidation_share_credit let a crafted debt_payments vector (duplicate HubAssetKeys, a leg the account does not owe, dust, a fee-measured shortfall, a sub-3-decimal whole-unit leg) or SeizeMode::Credit into the liquidator's own account take the borrower's collateral, pull pool cash, or credit supply shares that no token backs.",
    "Critical. A borrower draws debt or withdraws collateral that the account cannot support, leaving bad debt for suppliers: process_borrow, process_withdraw, merge_debt_leg, merge_withdraw_leg, enforce_post_pool_solvency, require_post_pool_risk_gates, calculate_account_risk_totals, sum_debt_usd, calculate_ltv_collateral_wad, the Context price and index cache, leg_may_restamp_risk_params and the min_borrow_collateral_usd floor let a multi-leg batch, a repeated asset, a same-token market in another hub, a stale cached LTV or liquidation threshold on an existing position, or a withdraw-all (amount 0) path skip or mis-evaluate the final health-factor check.",
    "Critical. A user extracts pool cash that no supplier or repayment funded, through share and index rounding or book mixing: calculate_scaled_supply, unscale_supply_floor, unscale_borrow_ceil, resolve_withdrawal, resolve_repay, resolve_net_settle, mint_supply / burn_supply / mint_debt / burn_debt, resolve_close_or_partial, withhold_liquidation_fee, credit_cash / debit_cash and require_backed_market let repeated tiny supply, withdraw, borrow or repay calls, a first supplier in a fresh market, or two hubs listing the same token (separate books, one physical balance) withdraw more tokens than were credited, repay less than the debt removed, or pay one hub's suppliers with another hub's cash.",
    "Critical. A flash loan or flash position is not repaid, or its callback mutates accounting mid-flight: pool ops/flash.rs prepare, invoke_receiver, collect_repayment and require_balance, controller process_flash_loan, process_flash_position, mint_and_forward, collect_collateral_deposits, require_flash_position_still_open, refund_listed_assets, with_flash_guard and require_not_flash_loaning let an attacker's Wasm receiver re-enter supply, repay, liquidate, recapitalize, update_indexes, claim_revenue or a second flash path, count the borrowed principal as its own collateral or repayment, get refunded balances the controller held before the call, or finish holding flash-minted debt with no supply behind it.",
    "Critical. An account strategy converts the controller's or the pool's funds into the caller's gain: swap_tokens, verify_router_output, balance_delta_since, refund_controller_balance_delta, process_multiply, process_swap_debt, process_swap_collateral, process_repay_debt_with_collateral, net_settle_collateral_against_debt, withdraw_and_swap_from_supply, repay_debt_from_controller and strategy_finalize trust a caller-supplied route whose pool addresses nobody allowlists, so an attacker's own venue contract on the call stack can inflate the measured output, pre-fund or drain the controller between snapshot and measurement, make close_position erase debt it did not repay, or credit collateral that never arrived, while the account still passes its final risk check.",
    "Critical. An attacker moves an on-chain price the aggregator trusts and borrows against it or liquidates with it: fair_lp_price_wad, the stable-pool pricing in lp_stable.rs, providers/aquarius.rs read and attest, engine resolve / blend / compose / read_source, tolerance and sanity-band checks, session cache, observation timestamp and decimal scaling let a same-transaction Aquarius swap, deposit, withdrawal or direct token donation (funded by the pool's own flash_loan) change LP reserves or total shares, or let a stale / future / mis-scaled Reflector or RedStone-format observation pass, so LP or asset collateral is overvalued to borrow and leave bad debt, or a healthy account is marked liquidatable.",
    "Critical. Bad-debt cleanup, socialization or recapitalization moves value to the wrong party: is_socializable_bad_debt, clean_bad_debt_standalone, execute_bad_debt_cleanup, socialize_bad_debt, check_bad_debt_after_liquidation, absorb_supply_as_revenue, the supply-index write-down, backing_shortfall / require_backed_market and pool recapitalize let an attacker clean an account that is not below the dust threshold or not insolvent, force a write-down onto suppliers after a self-made insolvency, supply right after a write-down to capture a recapitalization, or leave debt that is neither repaid nor socialized.",
    "Critical. An unprivileged address acts on an account it does not control or erases an account's debt: require_owner_or_delegate, require_account_owner, is_owner_or_delegate, add_delegate / set_account_delegate with the stamped grant owner, require_third_party_existing_supply, create_account / load_or_create_account with account_id 0, require_spoke_match, resolve_seize_receiver, cleanup_account_if_empty, remove_account_and_burn_nft, the position NFT transfer / transfer_from / approve paths and nft burn let an attacker borrow or withdraw from a victim account, open a foreign asset slot, re-bind a spoke, burn or delete an account while debt remains, or reuse an account id or NFT to inherit another user's collateral.",
    "High. A permissionless keeper or maintenance call breaks accounting or pushes accounts into liquidation: update_indexes with its chunked accrual (compound, curve, index, simulate), claim_revenue with require_revenue_backed and burn_claimable_revenue, update_account_threshold with favors_liquidator / clears_min_hf / restamp_listed_supply_ltv, enforce_spoke_cap and the scaled cap conversion, and governance execute / execute_self / execute_canceller_reset callable by anyone once an operation is ready let an attacker choose timing or arguments that overstate revenue against supplier cash, shrink or inflate an index, restamp a victim's liquidation threshold into HF < 1, bypass a supply or borrow cap, or execute a ready operation with other arguments, out of predecessor order or after its grace window.",
    "Critical/High blind spot. A normal user, liquidator or flash receiver abuses an assumption XOXNO Lending never wrote down: a price, index or listing flag cached in Context and reused after a pool call has changed it; a guard present on supply/borrow but missing on multiply, flash_position, migrate_from_blend or repay_debt_with_collateral; an i128 or RAY/WAD/BPS unit mix at an extreme but reachable value; a HubAssetKey whose token equals the pool, controller or another hub's token; a Soroban auth tree, TTL archival or storage key that lets one account read or overwrite another's entry; an account emptied, deleted or re-created inside one transaction; or a zero-amount, zero-decimal or whole-unit edge the formulas only proved safe away from the boundary - yielding theft of user funds, unbacked debt, protocol insolvency or funds frozen with no permissionless exit.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one XOXNO Lending target.

    ```
    target_file format:
    "'File Name: contracts/controller/src/positions/liquidation/math.rs -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit questions for this exact XOXNO Lending target:

    {target_file}

    Project focus:
    XOXNO Lending is a Stellar Soroban money market. The controller owns accounts (one position NFT each, bound to one spoke) and all risk: supply, borrow, withdraw, repay, pro-rata liquidation with a bonus curve and Transfer/Credit seizure, bad-debt cleanup, cash flash loans, flash positions, and router strategies (multiply, swap_debt, swap_collateral, repay_debt_with_collateral, migrate_from_blend). One pool holds every token and keeps per-market (hub, token) books: cash, RAY supply/debt shares, indexes, revenue. The price aggregator resolves Reflector, RedStone-format and Aquarius LP sources with dual-leg tolerance and sanity bands. Units: token amounts, WAD (USD, HF), RAY (shares, indexes, rates), BPS.

    Rules:
    * Treat `File Name:` as the exact file and `Scope:` as the ONLY impact to target.
    * Assume full repo context. Do not ask for code or say anything is missing.
    * Use exact Rust symbols (fn, struct, enum variant, storage key, error) when possible.
    * Attacker is unprivileged only: any funded Stellar account or its own deployed Wasm contract that calls controller supply, borrow, withdraw, repay, liquidate, clean_bad_debt, flash_loan, flash_position, multiply, swap_debt, swap_collateral, repay_debt_with_collateral, migrate_from_blend, update_indexes, claim_revenue, update_account_threshold, recapitalize, add/remove_delegate on its own account, position-nft transfer/approve/renew, governance execute on an already-ready operation; that sends tokens directly to the pool or controller; that trades or provides liquidity on Aquarius/Soroswap/Blend itself; and that supplies its own flash receiver or swap route bytes.
    * Attacker is NOT the governance owner or a PROPOSER, EXECUTOR, CANCELLER, GUARDIAN or ORACLE role, not an XOXNO oracle signer, not the router admin, not a governance-approved position manager, not the issuer of a listed token, and holds no victim key or NFT approval. Never assume malicious admin, upgrade, bad listing parameters, leaked key or social engineering.
    * Out of scope, never ask about: swap-aggregator, xoxno-oracle and defindex-strategy internals, keeper/exporter services, scripts, configs, Stellar/Soroban host bugs, validators or peers, third-party oracle honesty within its sanity band, listed-token semantics (fee-on-transfer, rebase, clawback), route quality, slippage and MEV ordering, operations that fail closed (pause, flags, cash shortage, price outage, TTL archival, budget limits), centralization, and the documented ADR choices (rounding direction, supply-index loss, cleanup, zero-fee flash position, full-close without HF-improvement guard).
    * Ignore test files, mocks, certora specs, vendor and generated code.
    * Every question must be a real transaction sequence the attacker submits: named entrypoint, exact arguments (account_id, HubAssetKey, amounts, SeizeMode, swap bytes, receiver), required account and market state. No unbounded-loop, memory, CPU-budget or "huge input" questions.
    * Generate 40 to 80 high-signal questions, at least 70% aimed at Critical impact. No generic checklist items or repeated root causes.
    * Every question must be testable with a Rust unit or integration test in tests/test-harness (make test-match PATTERN=...) or a proptest.

    Core invariants:
    * Solvency: after every risk-increasing call the account HF >= 1 WAD at strict prices; no borrow or withdraw leaves unbacked debt.
    * Liquidation coupling: seized value <= repaid debt * (1 + capped bonus); only HF < 1 accounts are liquidatable; repaid debt is really retired.
    * Custody: tokens paid out of a market never exceed its booked cash; credit follows measured receipt; account books reconcile with pool totals.
    * Authority: only the NFT owner or an active listed delegate moves an account's funds; third parties cannot open foreign asset slots.
    * Flash: principal plus fee is back before return; no callback re-enters a monetary flow.

    Each question must include:
    1. target function;
    2. attacker action (exact call and arguments);
    3. preconditions (accounts, positions, prices, market cash, hub/spoke listing);
    4. execution sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger EXECUTION_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: test-harness test PARAMETERS and assert SOLVENCY, LIQUIDATION_COUPLING, CUSTODY, AUTHORITY, or FLASH.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused XOXNO Lending exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: any funded Stellar account or its own Wasm contract calling the controller's user and permissionless entrypoints (supply, borrow, withdraw, repay, liquidate, clean_bad_debt, flash_loan, flash_position, multiply, swap_debt, swap_collateral, repay_debt_with_collateral, migrate_from_blend, update_indexes, claim_revenue, update_account_threshold, recapitalize) on accounts it owns or third-party-allowed paths, position-nft transfer/approve, governance execute on a ready operation, sending tokens directly to contracts, trading on Aquarius/Soroswap itself, and supplying its own flash receiver or swap route.
- Reject governance owner, role holder, oracle signer, router admin, position manager, token issuer, upgrade, leaked-key and bad-parameter paths.
- Reject swap-aggregator, xoxno-oracle, defindex-strategy, services, scripts and configs; Stellar/Soroban host bugs; third-party oracle prices within sanity band, source count and staleness; listed-token semantics; route quality, slippage and MEV; fail-closed operations (pause, flags, cash shortage, price outage, TTL archival, budget limits); centralization; documented ADR choices; test/mock/certora/vendor findings.
- Reject unbounded-loop, memory or CPU-budget claims.
- Focus on real impact: theft of user funds, permanent freezing of funds, protocol insolvency, theft or freezing of unclaimed yield, temporary freezing of funds.

## Validate
- Trace the exact path from the attacker's transaction through controller, pool and price aggregator with the arguments and state it supplies.
- Check existing guards: require_auth plus require_owner_or_delegate / require_account_owner, require_third_party_existing_supply, with_flash_guard and require_not_flash_loaning, enforce_post_pool_solvency, listing flags and caps, measured receipts, pool require_backed_market / require_utilization_below_max / require_liquidation_buffer, flash require_balance, dual-leg tolerance and sanity bands, i128 checked math, Soroban reentry rules.
- Confirm the path is reachable on the deployed configuration (configs/networks.json, docs/reference/architecture.md).
- Accept only concrete fund loss, frozen funds, unbacked debt or insolvency.
- Require exact file/function support and a reproducible test-harness PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker call and arguments, exploit flow, and why existing guards fail]

### Impact Explanation
[Concrete impact and severity: Critical (theft of user funds, permanent freezing of funds, protocol insolvency) or High (theft/permanent freezing of unclaimed yield, temporary freezing of funds)]

### Likelihood Explanation
[Preconditions, funding, account and market state, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[test-harness test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for XOXNO Lending.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production code only: contracts/controller, contracts/pool, contracts/governance, contracts/position-nft, contracts/price-aggregator, common, interfaces. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint. The analog must stand on XOXNO Lending's own code.
- Keep only analogs an unprivileged address can reach: controller supply/borrow/withdraw/repay/liquidate/clean_bad_debt/flash_loan/flash_position/multiply/swap_debt/swap_collateral/repay_debt_with_collateral/migrate_from_blend/update_indexes/claim_revenue/update_account_threshold/recapitalize, position-nft transfer/approve, governance execute of a ready operation, direct token transfers to the pool or controller, own trades on Aquarius/Soroswap, own flash receiver or swap route.
- Map the class onto XOXNO Lending's real shape:
  * Aave-v3/Compound-style shares: RAY supply/debt shares and indexes in pool cache/scale.rs, floor/ceil unscaling, revenue shares inside total supply, millisecond chunked accrual;
  * hub/spoke markets: separate books per (hub, token) over one physical pool balance; cached per-position LTV/threshold restamped by update_account_threshold;
  * WAD risk: health factor and min_borrow_collateral_usd from Context-cached strict prices and indexes;
  * liquidation: multi-leg pro-rata plan, HF-based bonus curve, whole-unit sub-3-decimal legs, SeizeMode::Transfer vs Credit share credit, excess-payment refund;
  * bad debt: dust-threshold cleanup, supply-index write-down, recapitalize without minting shares;
  * measured-receipt settlement and flash paths: exact-balance cash flash loan, flash_position debt minted before a callback, flash guard;
  * router strategies: one exact input-transfer auth, balance-delta output measurement, unallowlisted route venues;
  * pricing: dual-leg tolerance, sanity bands, Aquarius constant-product and stable LP fair value, Reflector/RedStone timestamps and decimals;
  * Soroban: require_auth trees, TTL/archival, storage keys, i128 overflow, restricted re-entry.
- Reject privileged, upgrade, leaked-key, bad-parameter, off-chain, services, swap-aggregator/xoxno-oracle/defindex internals, third-party oracle honesty within bands, token semantics, route quality/MEV, fail-closed DoS, budget/memory, documented ADR choices, and no-impact analogs.
- Critical, High and Medium only.

## Validate
- Map the class to the strongest path a single unprivileged address can submit, naming exact entrypoints and arguments.
- Prove root cause with exact file/function support.
- Accept only theft of user funds, permanent freezing of funds, protocol insolvency, theft or freezing of unclaimed yield, temporary freezing of funds, or a contract unable to operate from lack of token funds.

## Output (Strict)
If valid analog exists, output:

### Title
[Clear vulnerability statement] - ([File: file_path])

### Summary
### Finding Description
### Impact Explanation
### Likelihood Explanation
### Recommendation
### Proof of Concept

If not, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for XOXNO Lending security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and RESEARCHER.md for scope, exclusions, and valid impact classes.
- Scope is the Immunefi XOXNO program: controller, pool, governance, position NFT, price aggregator and shared math (contracts/controller, contracts/pool, contracts/governance, contracts/position-nft, contracts/price-aggregator, common, interfaces) on Stellar mainnet. mock/, tests/, certora/, vendor/, scripts/, services/, docs/, configs, web/API/SDK are out of scope.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the evidence proves the higher impact.
- Accepted impacts (Immunefi V2.3):
  * Critical: direct theft of any user funds, at-rest or in-motion, other than unclaimed yield; permanent freezing of funds; protocol insolvency.
  * High: theft of unclaimed yield; permanent freezing of unclaimed yield; temporary freezing of funds.
  * Medium: smart contract unable to operate due to lack of token funds.
  * Reject Low, informational and best-practice findings.
- Reject compromised governance, role, oracle-signer or keeper keys (unless the protocol makes the damage materially worse), documented admin paths, upgrades, and parameter values as such (logic that lets a parameter break an invariant is in scope).
- Reject bugs in Stellar, the Soroban host, the toolchain or third parties (Reflector, RedStone, DeFindex, Blend, swap venues, token contracts); how the protocol validates their responses is in scope.
- Reject listed-token behaviour (fee-on-transfer, rebase, clawback), route quality, slippage and MEV, oracle prices that pass sanity bands, source count and staleness, lack of liquidity, Sybil, centralization, scanner/lint output and missing events.
- Reject operations that fail closed or are blocked by pause, flags, cash shortage, TTL expiry or Soroban budget limits.
- Treat as known design, not findings on their own: ADR-0003 rounding, ADR-0012 supply-index loss, ADR-0021 cleanup, ADR-0009 spoke binding, ADR-0002 custody, ADR-0013 measured receipts, ADR-0004/0005 fail-closed dual-source pricing, ADR-0019 liquidation credit, ADR-0020 zero-fee flash position, ADR-0015 caps, ADR-0016 chunked accrual, ADR-0007/0008 halt flags and ratchet, is_collateralizable as an entry gate only, full NFT/delegate authority over the account, full-close liquidation without HF-improvement guard, solvency separate from liquidity, and the threat-model residual risks. Valid only if the impact goes beyond them.
- Reject if the exploit needs more than an unprivileged address can do: call controller user/permissionless entrypoints, position-nft transfer/approve, governance execute of a ready operation, send tokens to contracts, trade on external venues, or deploy its own receiver or route.
- Reject if already fixed, acknowledged or public. A runnable PoC is mandatory; prefer #NoVulnerability over speculation.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and a broken invariant from docs/reference/invariants.md (INV-AUTH, ACCT, IDX, ORACLE, RISK, LIQ, HALT, STOR, FLASH, STRAT).
3. Reachable path: preconditions (accounts, positions, prices, market cash, listing) -> submitted call and arguments -> trigger -> bad result.
4. Existing guards reviewed and shown insufficient: require_auth and owner/delegate checks, third-party supply restriction, flash guard, post-pool solvency, listing flags and caps, measured receipts, pool backing/utilization/liquidation-buffer guards, flash require_balance, dual-leg tolerance and sanity bands, checked i128 math, Soroban reentry rules.
5. Concrete accepted impact with realistic likelihood.
6. Reproducible PoC on a local fork or tests/test-harness.
7. No rejection reason from SECURITY.md, the program exclusions, known design choices, or privilege assumptions.

## Silent Triage Questions
Before output, internally answer:
- Can an ordinary address trigger this with no role, no signer key and no victim authorization?
- Does the code behave as claimed on the deployed configuration?
- Is the impact caused by XOXNO Lending's code, not a third party, the host, or an admin?
- Is it beyond the documented design choices and threat-model residual risks?
- Is the loss, freeze or insolvency concrete?
- What exact test proves it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the bug and impact]

## Finding Description
[Exact code path, root cause, exploit flow, and why existing guards fail]

## Impact Explanation
[Concrete impact, severity, and Immunefi V2.3 category]

## Likelihood Explanation
[Attacker capability, funding and state required, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or a test-harness test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt
