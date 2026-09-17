import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 10
# todo: the path from https://github.com/raydium-io/raydium-amm
SOURCE_REPO = "raydium-io/raydium-amm"
# todo: the name of the repository
REPO_NAME = "raydium-amm"
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
    # Instruction handlers: every entrypoint any wallet can call on the deployed AMM
    # =================================================================================
    "program/src/processor.rs",
    "program/src/instruction.rs",
    "program/src/entrypoint.rs",

    # =================================================================================
    # Pool accounting math: swap curve, decimal normalization, LP and pnl arithmetic
    # =================================================================================
    "program/src/math.rs",

    # =================================================================================
    # Pool state: AmmInfo, AmmConfig, TargetOrders loaders, status/state and fee gates
    # =================================================================================
    "program/src/state.rs",

    # =================================================================================
    # CPI wrappers moving vault tokens, LP supply and lamports under the AMM authority
    # =================================================================================
    "program/src/invokers.rs",

    # =================================================================================
    # Program wiring, errors and on-chain logs consumed by integrators
    # =================================================================================
    "program/src/lib.rs",
    "program/src/error.rs",
    "program/src/log.rs",
]


target_scopes = [
    "Critical. An attacker drains a pool's coin or pc vault by passing accounts the handler never binds to the loaded AmmInfo: the next_account_info ordering and check_assert_eq guards over amm_coin_vault, amm_pc_vault, amm_lp_mint, amm_authority and token_program in Processor::process_swap_base_in, process_swap_base_out, process_swap_base_in_v2, process_swap_base_out_v2, process_deposit and process_withdraw in program/src/processor.rs, Processor::authority_id and Processor::unpack_token_account, or Invokers::token_transfer_with_authority in program/src/invokers.rs let an attacker-owned token account, a fake mint, a spoofed token program or a mismatched nonce/bump stand in for a pool account and still be signed for by the AMM PDA.",
    "Critical. An attacker mints LP tokens that are not backed by deposited reserves, or deposits into one pool and redeems from another: Processor::process_deposit and process_withdraw in program/src/processor.rs, InvariantPool::exchange_token_to_pool and exchange_pool_to_token and InvariantToken::exchange_coin_to_pc/exchange_pc_to_coin in program/src/math.rs, and Invokers::token_mint_to / token_burn let the LP amount be computed from a supply, vault balance or deducted-pnl figure the attacker influences in the same transaction, so lp_mint.supply stops tracking the vault reserves.",
    "Critical. A swap leaves the pool with less value than it started with, letting an attacker extract reserves over one or a few transactions: Calculator::swap_token_amount_base_in and swap_token_amount_base_out, checked_ceil_div for u128 and U128, to_u64/to_u128, normalize_decimal, normalize_decimal_v2 and restore_decimal in program/src/math.rs, or the swap_fee computation and SwapDirection selection in the four swap handlers in program/src/processor.rs round, truncate, saturate or convert so that x*y after the swap is below x*y before it, or the fee is charged on the wrong side or skipped entirely.",
    "Critical. An attacker withdraws value belonging to LPs or the protocol through the pnl path: Processor::calc_take_pnl, process_withdrawpnl and the need_take_pnl_coin/need_take_pnl_pc accounting in StateData in program/src/state.rs let self-supplied vault balances, a stale or attacker-shaped TargetOrders account, or an unchecked pnl owner/config binding credit pnl that was never earned, double-count it across calls, or subtract it from the swap reserve twice so LP withdrawals become unbacked.",
    "Critical. An attacker permanently freezes a pool's deposits: a value that makes Processor::process_swap_base_in/out, process_deposit or process_withdraw always fail (an overflow or divide-by-zero on the next call, a zero or one-sided reserve, an lp supply forced to zero, a status or pool_open_time left in a non-swappable AmmStatus/AmmState), or a TargetOrders/AmmInfo field written on an error path, makes every later user transaction on that AmmInfo revert with no recovery available to an unprivileged holder of LP tokens.",
    "Critical. An attacker hijacks pool creation so a live pool is controlled or pre-drained by them: Processor::process_initialize2, TargetOrders::check_init, AmmInfo::initialize, StateData::initialize, Processor::get_associated_address_and_bump_seed and Invokers::create_ata_spl_token / token_set_authority in program/src/invokers.rs let the amm PDA, target_orders, lp_mint, vaults or authority nonce be supplied or seeded so an existing pool is re-initialized, an attacker-held mint authority survives, or the initial LP mint and the coin/pc amounts actually escrowed do not match.",
    "Critical. An attacker forges the AmmInfo, AmmConfig or TargetOrders account a handler trusts: AmmInfo::load_mut_checked and load_checked, AmmConfig::load_mut_checked and load_checked, TargetOrders::load_mut_checked and load_checked in program/src/state.rs, and the owner/data_len/status/discriminator checks around them accept an account of the right size owned by the program but never initialized, a config PDA that is not the AMM_CONFIG_SEED derivation, or a TargetOrders whose owner field does not point at the loaded AmmInfo, so pool parameters and balances are read from attacker-chosen bytes.",
    "Critical. An attacker reaches a state transition or admin-only effect without the required signer: the is_signer and config_feature::amm_owner / pnl_owner / collect_lamports comparisons in Processor::process_set_params, process_create_config, process_update_config, process_withdrawpnl and process_withdraw_excess_lamports in program/src/processor.rs, Fees::validate and AmmStatus::valid_status / AmmState::valid_state in program/src/state.rs, or the implicit status promotion from WaitingTrade to SwapOnly inside the swap handlers let an ordinary caller flip status, fees, pool_open_time or the config account, or move lamports out of accounts whose rent-exempt minimum they then break.",
    "High. An attacker steals from every other user of a pool by desynchronizing the reserves the curve reads from the tokens the vaults actually hold: Calculator::calc_total_without_take_pnl_no_orderbook in program/src/math.rs, the unpack_token_account/unpack_mint reads in program/src/processor.rs, direct donations to a vault, a wrapped-SOL vault resynced mid-instruction by Processor::withdraw_excess_lamports_from_token, or a coin/pc mint whose decimals or supply changes after AmmInfo::initialize make the swap, deposit or withdraw math price a trade off balances that are not the post-transfer truth.",
    "Critical/High blind spot. An ordinary swapper, liquidity provider or pool creator abuses an assumption the Raydium AMM never wrote down: a first or last liquidity provider taking a rounding or minimum-LP edge that the formula only proved safe for a funded pool, an AmmInfo field read again after the check that authorized it (reserves, lp supply, status, recent_epoch), a guard enforced in process_swap_base_in but missing in its _v2 twin or in the base_out variant, self-swap or self-transfer where user_source and user_destination alias each other or a vault, a decimals or sys_decimal_value assumption that breaks for extreme-decimal or fee-on-transfer-like mints, reentry through a token program supplied by the caller, dust or lamports stranded on an error path that still emits an encode_ray_log event integrators trust, or state left inconsistent by a partially applied instruction - yielding theft of user funds, unbacked LP minting, pool insolvency, or a pool that can never be swapped or withdrawn from again.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one Raydium AMM target.

    ```
    target_file format:
    "'File Name: program/src/processor.rs -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit questions for this exact Raydium AMM target:

    {target_file}

    Project focus:
    raydium-amm is the Solana constant-product AMM program deployed at 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8. Focus only on what an ordinary wallet reaches: sending Initialize2, Deposit, Withdraw, SwapBaseIn, SwapBaseOut, SwapBaseInV2 and SwapBaseOutV2 instructions with account lists and instruction data they fully choose, creating their own mints, token accounts and pools, and composing these calls with other programs inside one transaction. Downstream of that: AmmInfo/AmmConfig/TargetOrders loading, swap and LP math, pnl accounting, and the SPL token CPIs signed by the AMM authority PDA.

    Rules:
    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Rust symbols (fn, struct, enum, impl, field or const) when possible.
    * Attacker is unprivileged only: anyone who funds a Solana wallet and sends transactions, creates mints, token accounts and pools, provides or withdraws liquidity, swaps, and passes any account list and instruction data the program will accept. They control only their own keys.
    * Attacker is NOT the amm_owner, pnl_owner, collect_lamports authority, config admin, a validator or a leader, and holds no other user's key. Never assume a malicious validator, leaked key, privileged signer, non-default config_feature build, or social engineering.
    * Out of scope, never ask about: Solana runtime or SPL token program bugs, client SDKs, off-chain services, RPC, logging and monitoring, deployment, dependency versions, 51%/sybil/centralization, lack of liquidity, pure MEV ordering, and oracle data simply being wrong.
    * Ignore test files, mocks, benchmarks, docs, generated files, and config-only findings.
    * Every question must describe a real transaction the attacker actually submits: named instruction, the account list and data they supply, the pool and mints they rely on. No generic unbounded-allocation, memory-growth, compute-exhaustion or "what if the input is huge" speculation without a concrete payload and a concrete broken invariant.
    * Generate 40 to 80 high-signal questions.
    * At least 70% must target theft of user funds, permanent freezing of pool funds, unbacked LP minting, or pool insolvency.
    * Every question must be testable by a `cargo test` unit test over the math/state types or a `cargo test-sbf` / solana-program-test transaction against the program.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Account binding: every account a handler acts on is the one recorded in the loaded AmmInfo (or derived from program_id and its nonce), and privileged effects require the configured signer.
    * Curve soundness: after a swap, reserves times reserves never decreases against the pool, and the fee is charged once on the input side.
    * LP backing: lp_mint.supply always corresponds to the coin and pc actually escrowed in the vaults, minus recorded pnl, for every deposit and withdraw path.
    * Pnl integrity: pnl is credited once, only from realized pool surplus, and never from principal an LP can still withdraw.
    * User liveness: no user-submitted transaction can leave a pool in a state where swapping or withdrawing reverts forever.

    Each question must include:
    1. target function/method;
    2. attacker action (a concrete instruction: accounts, mints, amounts, data);
    3. preconditions (wallet balance, pool state, mints or token accounts the attacker created);
    4. execution sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger EXECUTION_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: cargo test / cargo test-sbf solana-program-test PARAMETERS and assert ACCOUNT_BINDING, CURVE_SOUNDNESS, LP_BACKING, PNL_INTEGRITY, or USER_LIVENESS.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused Raydium AMM exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: anyone who funds a wallet and sends AMM instructions with account lists and data they choose, creates their own mints, token accounts and pools, provides liquidity, or swaps. No amm_owner, pnl_owner, collect_lamports authority, config admin, validator, or foreign-key access.
- Reject privileged-signer, leaked-key, malicious-validator, non-default config_feature build, off-chain, RPC, client-SDK, deployment and misconfiguration-only paths.
- Reject Solana runtime and SPL token program bugs, 51%-style, sybil and centralization claims, lack of liquidity, pure MEV ordering, third-party oracle data simply being wrong with no manipulation path, best-practice critiques, and test/mock/docs/generated/config-only findings.
- Reject generic compute-exhaustion or allocation claims with no concrete instruction payload and no broken invariant.
- Focus on real on-chain impact: theft of user or LP funds, permanent freezing of pool funds, unbacked LP minting, pnl or reserve accounting that makes the pool insolvent, or an unauthorized state/parameter change.

## Validate
- Trace the exact reachable path from the attacker's transaction into the affected function, including the account list they supply.
- Check whether AmmInfo/AmmConfig/TargetOrders load_checked owner and status checks, check_assert_eq account bindings, authority_id PDA derivation, is_signer and config_feature owner checks, AmmStatus permission gates, Fees::validate, checked arithmetic and overflow-checks, or slippage checks already stop it.
- Confirm the path is reachable on the current mainnet build (default features, program id 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8) with the openbook orderbook path removed.
- Accept only concrete fund loss or freezing, unbacked LP mint, insolvent pool accounting, or an unauthorized privileged effect.
- Require exact file/function support and a reproducible cargo test or cargo test-sbf / solana-program-test PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker instruction and accounts, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact and severity: Critical (direct theft of user or LP funds, permanent freezing of funds, unbacked LP minting, protocol insolvency) or High (theft of unclaimed pnl or fees, temporary freezing of pool funds)]

### Likelihood Explanation
[Preconditions, wallet funding, pool state needed, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[cargo test / cargo test-sbf solana-program-test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for the Raydium AMM.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production program context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only analogs an unprivileged swapper, liquidity provider or pool creator can reach: Initialize2, Deposit, Withdraw and the four swap instructions, account-binding and PDA authority checks, AmmInfo/AmmConfig/TargetOrders loading, swap and LP math, decimal normalization, pnl accounting, or the SPL token CPIs in invokers.rs.
- Reject privileged-signer, leaked-key, malicious-validator, non-default build, off-chain, RPC, client-SDK, deployment, Solana-runtime, SPL-token-program, dependency-only, mocked-only paths, and no-impact analogs.
- Medium, High and Critical only; no low, best-practice, or compute-only analogs.

## Validate
- Map the bug class to the strongest reachable path from a single submitted transaction with attacker-chosen accounts and data.
- Prove root cause with exact file/function support.
- Accept only concrete theft or permanent freezing of user or LP funds, unbacked LP minting, insolvent pool accounting, or an unauthorized privileged effect.

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
    Generate a strict bounty-style validation prompt for Raydium AMM security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Scope is the deployed AMM program only: program/src/lib.rs, entrypoint.rs, instruction.rs, error.rs, invokers.rs, log.rs, math.rs, processor.rs, state.rs. Anything outside the on-chain program (SDKs, UI, off-chain services) is out of scope.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Focus on Critical and High; Medium is in scope only as Immunefi V2.3 defines it (contract unable to operate from lack of token funds, block stuffing, unprofitable griefing, theft of gas). Reject informational, best-practice and low findings.
- Reject malicious-admin, malicious-validator, leaked-key, privileged-signer, non-default config_feature build, off-chain, RPC, client-SDK, monitoring, logging, deployment, dependency-only, docs/style, generated-file, and test/mock/config-only issues.
- Reject if the exploit needs the amm_owner, pnl_owner, collect_lamports authority, config admin, a validator, another user's key, victim social engineering, or anything outside what an unprivileged wallet can put in a transaction's accounts and instruction data.
- Reject Solana runtime and SPL token program bugs, 51%-style majority attacks, sybil and centralization claims, lack of liquidity, pure MEV ordering the team already knows of, UI bugs, and third-party oracle data being wrong without a manipulation path.
- Reject if the bug was fixed, acknowledged, or publicly disclosed already, per the eligibility rules.
- A valid report must be triggerable by an unprivileged swapper, liquidity provider or pool creator, unless the claim proves escalation from that starting point.
- The final impact must map to an in-scope category: Critical - direct theft of user or LP funds, permanent freezing of funds, unbacked or unauthorized LP minting, or protocol insolvency; High - theft of unclaimed yield or pnl, or temporary freezing of funds; Medium - the pool unable to operate, unprofitable griefing, or theft of gas.
- A PoC is mandatory: prose alone is not accepted. Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken account-binding, curve-soundness, LP-backing, pnl-integrity, or user-liveness invariant.
3. Reachable exploit path: preconditions (wallet funding, pool state, attacker-created mints or token accounts) -> submitted instruction with its account list and data -> trigger -> bad result.
4. Existing load_checked owner and status checks, check_assert_eq account bindings, authority_id PDA derivation, is_signer and config_feature owner checks, AmmStatus gates, Fees::validate, checked arithmetic and slippage checks reviewed and shown insufficient.
5. Concrete in-scope Critical/High (or clearly-argued Medium) impact with realistic likelihood.
6. Reproducible proof path: cargo test unit PoC or cargo test-sbf / solana-program-test transaction sequence.
7. No obvious rejection reason from SECURITY.md, known issues, privilege assumptions, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can an ordinary wallet trigger this by sending an AMM instruction with accounts and data it chooses, without any configured authority or foreign key?
- Does the code actually behave as claimed on the current mainnet build, with the openbook orderbook path removed?
- Is the impact caused by this program, not by the Solana runtime, the SPL token program, or a privileged actor?
- Is the fund loss, unbacked mint, insolvency or freeze concrete rather than hypothetical?
- Would an Immunefi triager accept the proof-of-concept?
- What exact test would prove it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the bug and impact]

## Finding Description
[Exact code path, root cause, exploit flow, and why existing checks fail]

## Impact Explanation
[Concrete in-scope impact, severity rationale, and Immunefi V2.3 category]

## Likelihood Explanation
[Attacker capability, funding and pool state required, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or cargo test / cargo test-sbf solana-program-test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt
