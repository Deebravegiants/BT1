import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = 'Zest-Protocol/zest-v2-contracts'
# todo: the name of the repository
REPO_NAME = 'zest-v2-contracts'

run_number = os.environ.get('GITHUB_RUN_NUMBER', '0')


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
    # LENS: VALUE FLOW AND CONSERVATION.
    # This variant follows the money only. Every file below is a place where tokens,
    # shares, or debt units are created, destroyed, converted between representations, or
    # moved between principals. A question belongs here only if it can be closed by an
    # arithmetic identity that must hold before and after a call.
    # =================================================================================

    # -- The two ledgers that must agree ----------------------------------------------
    # market: converts token amounts <-> USD <-> scaled debt, and is the only mover of
    # user value. market-vault: the per-user side of the ledger (collateral map, debt map)
    # and the custodian of all plain collateral. NOTHING in the protocol ever sums the
    # per-user ledger and compares it to the vault aggregate, so a single bad write is
    # permanent and compounds with every accrual.
    "mainnet/contracts/market/v0-4-market.clar",
    "mainnet/contracts/market/v0-market-vault.clar",

    # -- Where shares and debt units are minted and burned ----------------------------
    # ft-mint? / ft-burn? of zft, the `assets` / `total-borrowed` / `principal-scaled`
    # vars, index accrual, treasury LP minting, socialize-debt write-down, flashloan fee.
    # v0-vault-stx is the native-STX path through .wstx and `as-contract? ((with-stx amt))`;
    # v0-vault-sbtc is the 8-decimal case that breaks decimal-symmetric assumptions;
    # v0-vault-ststx carries an underlying whose own value drifts against the share price.
    # usdc / usdh / ststxbtc are byte-identical to these apart from constants.
    "mainnet/contracts/vault/v0-vault-stx.clar",
    "mainnet/contracts/vault/v0-vault-sbtc.clar",
    "mainnet/contracts/vault/v0-vault-ststx.clar",

    # -- Decimals: the multiplier on every value computation --------------------------
    # `decimals` is captured once at `insert` via call-get-decimals and never re-read.
    # Every USD figure in the protocol divides by (pow u10 decimals).
    "mainnet/contracts/registry/v0-assets.clar",

    # =================================================================================
    # NOT IN THIS VARIANT:
    # * The whole dao directory. Any impact requiring DAO compromise is out of scope, and the
    #   treasury is only ever credited by `accrue`, which is audited here from the vault side.
    # * v0-egroup - risk parameters, not value math; covered by another lens.
    # * FLASHLOANS. Out of scope protocol-wide: never target `flashloan`, its fee, its
    #   permission whitelist or `in-flashloan`. A flashloan may fund an attack, never be one.
    # * local-testing/**, Pyth and Wormhole, v0-1-data.clar, traits, proposals, docs, .toml.
    # =================================================================================
]


target_scopes = [
    "Critical. THE UNRECONCILED LEDGERS. Sum over all users of the market-vault `debt` map times the vault `index` must equal the vault's own `total-debt` (`calc-cumulative-debt` of `principal-scaled`), yet the two are written by different contracts with different rounding: market `convert-to-scaled-debt` rounds the user's scaled debt UP while vault `system-borrow` computes its own `scaled-amount` with `mul-div-up` against the same `index`, and `repay` / `system-repay` shrink them with unrelated formulas. Show a borrow-repay cycle after which the per-user total and the vault aggregate differ, and compound it until the vault reports solvency it does not have.",

    "Critical. CUSTODY VERSUS LEDGER. The tokens actually held by .v0-market-vault must equal the sum of its `collateral` map for that asset. `receive-tokens` / `send-tokens` move them, `add-user-collateral` / `remove-user-collateral` record them, and in `collateral-remove` the map is decremented and `insert` is written BEFORE `send-tokens` runs. Show any path where a transfer succeeds without the matching map write, or the map write survives a transfer that moved a different amount, and drain the surplus or strand the deficit.",

    "Critical. TWO NAMES FOR ONE DEBT. `principal-scaled` and `total-borrowed` both describe outstanding principal but are updated by three different rules: `system-borrow` adds `mul-div-up amount INDEX-PRECISION idx` to one and raw `amount` to the other; `system-repay` reduces the first by `calc-principal-ratio-reduction` and the second by `capped-amount x total-borrowed / debt`; `socialize-debt` reduces the first by `scaled-amount` and the second by `scaled-amount x borrowed / scaled-principal`. Drive them apart so `total-debt` exceeds `total-borrowed` by phantom interest, or `total-borrowed` survives after `principal-scaled` hits zero, and show the effect on `total-assets` and therefore on every share price.",

    "Critical. INTEREST THAT NEVER EXISTED. `total-assets` adds `(- debt borrowed)` as accrued interest whenever debt exceeds borrowed, and that figure feeds `convert-to-assets-preview` for every redeemer. The difference is not backed by any token in the vault until a borrower actually repays. Show a state where `total-assets` counts interest on debt that has been socialized away, on a position already liquidated, or on principal that `system-repay` removed from `total-borrowed` without removing from `principal-scaled`, so early redeemers withdraw at an inflated share price and the last suppliers absorb the hole.",

    "Critical. ZERO SHARES FOR REAL TOKENS. `convert-to-shares-preview` returns `u0` when `total-assets-preview` is non-zero and `total-supply` is zero (the `(if (is-eq ta u0) u0 ...)` branch after the supply check), and `deposit` only enforces `(>= inkind min-out)`. Show a reachable vault state - after a full redeem that leaves residual `assets`, after socialization, or after a treasury-LP-only supply - where a depositor transfers underlying and is credited zero or near-zero shares, permanently donating its principal to whoever holds the remaining supply.",

    "Critical. THE SOCIALIZATION APPLIES TWO DIFFERENT LOSSES. One bad-debt event writes down `lindex` by the ratio `(- old-total-assets debt-reduction) / old-total-assets` but reduces `assets` by `principal-reduction`, a completely different quantity derived from `scaled-amount x borrowed / scaled-principal`. Show that the loss charged to suppliers through the share price and the loss removed from the vault's asset base disagree, so either the vault claims assets it lost or it destroys value the loss never justified, and quantify the drift over repeated socializations.",

    "Critical. DEBT THAT CANNOT BE REPAID. `convert-to-scaled-debt` rounds the borrower's scaled debt UP, `repay` caps at `max-repay-tokens` computed with `mul-div-up` then converts back with `mul-div-down`, and `remove-user-scaled-debt` deletes the row only on an exact zero. Show a borrow amount and index value for which the final unit of scaled debt can never be cleared, so the debt bit stays set in the position mask, the egroup never relaxes, and every unit of collateral behind it is permanently frozen.",

    "Critical. THE SEIZURE DOES NOT BALANCE. In one liquidation the borrower loses `coll-final`, the liquidator pays `debt-to-repay`, the vault records `scaled-to-remove`, and any remainder may be socialized. `calc-final-liquidation-amounts` recomputes debt from capped collateral with `calc-liq-debt-repay-real`, then `scale-debt-for-liquidation` re-scales collateral again by `scaled-to-remove / scaled-debt`. Show a case where collateral leaving the borrower exceeds debt cleared times (BPS + liq-penalty), or where debt is cleared that nobody paid for, and name which party absorbs the difference.",

    "Critical. DOUBLE COUNTING ACROSS THE ZTOKEN BOUNDARY. One deposit of underlying becomes vault `assets` backing zft shares AND, once pledged, a collateral row valued by `resolve-ztoken` at `lindex` times the share amount. The same economic value now supports a share redemption and a borrow at the same time. Establish whether the pledged shares are actually held by .v0-market-vault and therefore removed from the redeemable float, or whether `supply-collateral-add`, `collateral-remove-redeem` and `liquidate-redeem` leave a window in which one unit of underlying backs two claims. Impact: protocol insolvency.",

    "Critical. THE TREASURY IS PAID IN SHARES NOBODY ACCOUNTED FOR. `accrue` mints `treasury-lp` zft to .dao-treasury computed as `reserve-inc x total-supply / (- total-assets-preview reserve-inc)`, while `total-supply-preview` adds that same not-yet-minted figure to the live supply used by BOTH conversion previews. Show that the shares minted are worth more than `reserve-inc` of assets at the post-mint price, that the same fee is counted twice within one transaction, or that the subtraction underflows and aborts `accrue`, freezing every function in the vault.",

    "High. DECIMAL TRUNCATION DESTROYS VALUE. Every USD figure is produced by `normalize`, which divides by `(pow u10 decimals)` AFTER multiplying amount by price, so the protocol's USD unit is a whole dollar. With an 8-decimal asset such as sBTC and a 6-decimal asset such as USDC in one position, show a collateral holding that normalizes to zero USD while still being seizable, a debt that normalizes to zero and therefore passes `is-healthy` for free, or an amount-price pair whose round-down on collateral and round-up on debt open a persistent free-borrow window.",

    "High. REDEEM AND DEPOSIT ARE NOT INVERSES. `deposit` increments `assets` by the raw `amount` received, `redeem` decrements it by `inkind` derived from the share price, and both call `accrue` first so the price moves between them. Show a deposit-then-redeem in the same block that returns more underlying than went in, or a rounding direction in `convert-to-shares-preview` versus `convert-to-assets-preview` that lets a loop of small deposits and redeems extract a unit per iteration until the vault's `assets` no longer matches its balance.",

    "High. THE SAME BORROW IS SCALED TWICE. market computes `scaled-debt-added` via `convert-to-scaled-debt asset-id amount true` from the cached `index`, while the vault independently computes `scaled-amount` via `mul-div-up amount INDEX-PRECISION idx` from its own `index` inside `system-borrow`. Both claim to represent the same principal. Show a case where the cached index and the live index differ, or the two roundings differ, so the user's recorded obligation and the vault's recorded receivable are not the same number, and repeat it to open a gap.",

    "High. REPAY ON BEHALF OF ANOTHER PRINCIPAL SPLITS PAYER FROM DEBTOR. `repay` pulls `amount-to-repay` from `contract-caller` via `vault-system-repay` but clears `repaid-scaled-debt` from `on-behalf-of`, with the token amount recomputed twice (`mul-div-up` after `mul-div-down`). Show a repayment where the tokens delivered to the vault are strictly less than the value of the scaled debt erased, or where the vault's `assets` is credited with `interest-paid` that the payer never provided.",

    "High. CAPS ARE COMPARED AGAINST THE WRONG QUANTITY. `deposit` checks `(<= (+ current-assets amount) CAP-SUPPLY)` against the `assets` var rather than `total-assets`, and `system-borrow` checks `(<= (+ debt amount) CAP-DEBT)` against `total-debt` which includes accrued interest. Show a sequence that pushes real deposits or real debt past the intended ceiling, or one where accrued interest alone trips `CAP-DEBT` and permanently blocks every borrow while positions still need to be refinanced.",

    "High. THE REDEEM PATH LEAVES THE VAULT SHORT. `redeem` gates on `(>= current-assets inkind)` and `(>= available-assets inkind)` where `get-available-assets` reads the real balance, then burns shares and calls `send-underlying`. Show a state - after a socialization that zeroed `assets` by saturating subtraction, after `accrue` minted treasury shares against an asset base that did not grow, or after `system-repay` credited only `interest-paid` - where these two guards disagree with each other so a redeem either aborts permanently for the last suppliers or succeeds beyond what the vault holds.",

    "High. THE COMPOSITE ENTRY POINTS MOVE VALUE TWICE. `supply-collateral-add` transfers underlying to the market, deposits it under an `as-contract?` post-condition scope, mints shares to the user, then adds `shares-minted` as collateral; `collateral-remove-redeem` removes `amount` of zToken collateral to the market and then redeems the SAME `amount` as shares. Show a mismatch between `shares-minted` and the amount subsequently pledged, or between the shares removed and the shares redeemed, that leaves value stranded in the market contract or lets a caller redeem shares it never pledged.",

    "High. WRAPPED STX IS AN EXTRA HOP. v0-vault-stx alone routes value through `.wstx` with `receive-underlying` / `send-underlying` under `as-contract? ((with-stx amt))`, while `ubalance` asks `.wstx` for the balance. Show a divergence between the vault's wSTX balance, its native STX balance, and its `assets` var - a partial wrap, a transfer that lands on the wrong principal, or a post-condition scope that permits a second movement - and turn it into an over-withdrawal or a permanently unredeemable supply.",

    "High. LIQUIDATION LEAVES ORPHANED OBLIGATIONS. After `socialize-debt-asset` walks the borrower's debt list, and after collateral has been fully seized, check what remains: `debt` rows for assets not in the socialized list, `collateral` rows at zero that were never `map-delete`d, and mask bits that were never cleared. Show a fully liquidated position that still carries an obligation or a mask bit, so it cannot be re-used, cannot be closed, and keeps accruing interest that `total-assets` counts as a supplier asset forever.",

    "High. THE RESERVE FEE IS TAKEN FROM THE WRONG BASE. `accrue` derives `reserve-inc` from `debt-delta` computed as `mul-div-down scaled-principal next` minus `mul-div-down scaled-principal idx`, both rounded down, while the borrower's own debt grows by `mul-div-up` on their scaled balance. Show that the interest charged to borrowers and the interest distributed to suppliers plus treasury do not sum to the same figure, and that the residue accumulates in - or is drained from - the supplier pool with every accrual.",

    "Critical. THE MISSING RECONCILIATION - what nobody built. There is no function anywhere in this protocol that sums the per-user ledger and compares it against the vault aggregate, no invariant check at the end of any state-changing call, and no way to detect drift after the fact. Identify the FIRST write that can desync the two ledgers under an ordinary user transaction, prove it numerically in one test (sum of `debt` map times `index` versus `total-debt`; sum of `collateral` map versus token balance; sum of zft balances times share price versus `total-assets`), and show that once desynced the protocol never notices, never corrects, and compounds the error at every accrual.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate conservation-focused audit questions for one Zest v2 target.

    ```
    target_file format:
    "'File Name: mainnet/contracts/vault/v0-vault-stx.clar -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate value-conservation security audit questions for this exact Zest Protocol v2 target:

    {target_file}

    Project focus:
    Zest v2 is a Clarity lending market on Stacks. Value exists in four representations and is
    constantly converted between them: underlying tokens held by a vault or by .v0-market-vault;
    zft shares minted by a vault; scaled debt units stored per user in market-vault and in
    aggregate as `principal-scaled` / `total-borrowed`; and USD notionals produced by `normalize`
    from an oracle price and a per-asset `decimals`. The market converts between all four on every
    call. Two independent ledgers track the same debt - the per-user `debt` map and the vault's
    own aggregate - and NOTHING reconciles them. Interest is created by `accrue` moving `index`
    and `lindex`, taken partly as `reserve-inc` minted to .dao-treasury as fresh shares, and
    destroyed by `socialize-debt`.

    Rules:
    * Treat `File Name:` as the exact contract.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Clarity symbols (define-public/private/read-only names, map, data-var, constant).
    * EVERY question must be answerable by an arithmetic identity that holds before and after a
      call. State the identity explicitly. Narrative questions with no closing equation are rejected.
    * Attacker is unprivileged only: an ordinary Stacks principal that funds a wallet, calls any
      public function, deploys its own Clarity contract, passes it as `<ft-trait>` or
      `<flash-callback>`, supplies its own `price-feeds`, and controls amounts, receivers,
      `on-behalf-of` and call ordering within a block.
    * Attacker is NOT a DAO signer, executor, market impl, authorized contract, miner, oracle
      publisher or node operator. Ignore malicious-miner, chain-reorg, MEV-only, governance-key,
      leaked-key and social-engineering assumptions.
    * PROGRAM EXCLUSIONS - a question landing in any of these wastes the whole batch:
      - ANY logic related to flashloans is OUT OF SCOPE. A flashloan may be used as a source of
        capital for a different attack, but never target `flashloan` itself, its fee, its
        `flashloan-permissions` / `default-flashloan-permissions` whitelist, or `in-flashloan`.
      - Liquidation of disabled collateral, and any other deliberate protocol safety design
        decision, is OUT OF SCOPE.
      - Anything requiring DAO compromise, or an accidental or incorrect registry update by the
        DAO, is OUT OF SCOPE. Full DAO control of the asset and egroup registries is intended
        design, and every egroup invariant needing global market and position knowledge is
        verified off-chain by the DAO before approval. Assume both registries are correctly
        configured, and target only the read and resolution paths an ordinary user call executes.
      - Also excluded everywhere: leaked keys or credentials, privileged addresses, external
        stablecoin depegs the attacker did not cause through a bug in this code, 51% and basic
        economic or governance attacks, Sybil attacks, centralization risk, lack of liquidity,
        incorrect data supplied by third-party oracles, best-practice notes, feature requests,
        and test or configuration files.
      - Oracle manipulation caused by a bug in THIS code remains fully in scope.
    * IN-SCOPE IMPACTS - every question must land on one and name it:
      Critical: direct theft of user funds at rest or in motion, other than unclaimed yield;
      permanent freezing of funds; protocol insolvency.
      High: theft of unclaimed yield or royalties; permanent freezing of unclaimed yield or
      royalties; temporary freezing of funds.
    * Ignore Pyth and Wormhole internals, a real oracle publishing wrong data, external stablecoin
      depegs, tests, mocks, `local-testing/**`, deployment plans, `.toml`, docs, read-only
      aggregators, gas and style, and dependency-only issues.
    * Every question must be a concrete real-world scenario an unprivileged principal can execute
      on mainnet with its own capital. No speculative unbounded-list, memory or resource-hygiene
      questions.
    * Clarity `+` `-` `*` abort on overflow and underflow. An abort is a finding only when it
      permanently blocks a funds path - say which one.
    * Generate 30 to 40 high-signal questions.
    * At least 70% must land on a Critical impact - direct theft of user funds, permanent
      freezing of funds, or protocol insolvency - rather than a High one.
    * Every question must be testable by a Clarinet / vitest simnet test in `local-testing/tests`
      against a local fork. Never propose testing on mainnet or a public testnet.
    * Avoid generic checklist questions and repeated root causes.
    * Prefer questions that name TWO quantities that must be equal and ask whether they are: a
      per-user total and its aggregate, a mint and its backing, an amount pulled and an amount
      credited, a round-up and its paired round-down, a fee charged and a fee distributed.

    Known dead ends - do NOT generate questions about these:
    * Governance setting a bad cap, fee, LTV, penalty or interest curve.
    * An external oracle or token behaving badly on its own.
    * A user harming only their own position with no third party and no protocol invariant broken.
    * Findings requiring the attacker to already be an authorized contract, market impl or signer.
    * Anything only reproducible against mock tokens or the mock oracle.

    Core identities (each question must close on one):
    * SHARE BACKING: sum of zft balances converted at the current share price never exceeds
      `total-assets`, and `assets` never exceeds the underlying the vault actually holds.
    * DEBT AGREEMENT: sum over users of the market-vault `debt` map times `index` equals the
      vault's `total-debt`.
    * CUSTODY: tokens held by .v0-market-vault equal the sum of its `collateral` map per asset.
    * FLOW CLOSURE: in any single call, value leaving equals value entering plus value minted
      minus value burned, with every party named.
    * ROUNDING DIRECTION: every conversion rounds against the user, and each round-up has a
      paired round-down that cannot be exploited by repetition.

    Each question must include:
    1. target function/method;
    2. attacker action (a concrete contract call with arguments);
    3. preconditions (funded principal, vault state, existing position);
    4. call sequence;
    5. the identity that breaks, written as an equation;
    6. scoped impact and who absorbs the loss;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, breaking the identity IDENTITY_EQUATION, causing scoped impact: SCOPE_IMPACT absorbed by PARTY? Proof idea: Clarinet simnet test PARAMETERS and assert SHARE_BACKING, DEBT_AGREEMENT, CUSTODY, FLOW_CLOSURE, or ROUNDING_DIRECTION.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a conservation-focused Zest v2 exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: an ordinary Stacks principal that funds a wallet, calls any public function, deploys its own Clarity contract and passes it as `<ft-trait>` or `<flash-callback>`, supplies its own `price-feeds`, and controls amounts, receivers, `on-behalf-of` and call ordering. No DAO signer, executor, market impl, authorized contract, miner, oracle publisher or node operator access; no leaked keys.
- Reject malicious-miner, chain-reorg, MEV-only, privileged-address, leaked-key and oracle-publisher paths.
- OUT OF SCOPE, reject on sight: any flashloan logic (`flashloan`, its fee, its permission whitelist, `in-flashloan`) - though a flashloan used purely as capital for a different attack is fine; liquidation of disabled collateral and other deliberate safety design decisions; anything requiring DAO compromise or an accidental or incorrect DAO registry update, since full DAO control of the asset and egroup registries is intended design and egroup invariants needing global position knowledge are verified off-chain before approval.
- Also reject: leaked keys, privileged addresses, external stablecoin depegs the attacker did not cause through a bug here, 51% / basic economic / governance attacks, Sybil, centralization risk, lack of liquidity, incorrect data supplied by third-party oracles, best-practice notes, feature requests, and test or configuration files. Oracle manipulation caused by a bug in THIS code stays in scope.
- The impact must be one of: Critical - direct theft of user funds at rest or in motion other than unclaimed yield, permanent freezing of funds, or protocol insolvency; High - theft of unclaimed yield or royalties, permanent freezing of unclaimed yield or royalties, or temporary freezing of funds.
- Reject Pyth/Wormhole internals, third-party token behaviour, external stablecoin depegs, `local-testing/**`, tests, mocks, deployment plans, docs, read-only aggregators, and dependency-only findings.
- Focus on real impact: protocol insolvency, direct theft of principal or unclaimed yield, permanent freezing of funds, or value minted from nothing.

## Validate
- Write the identity the question claims is broken as an explicit equation over named state variables BEFORE tracing any code.
- Trace the exact reachable path from the attacker's call (function, arguments, trait principal, price-feeds, receiver, on-behalf-of, ordering) and record every read and write to `assets`, `principal-scaled`, `total-borrowed`, `index`, `lindex`, the zft supply, the `collateral` and `debt` maps, and the real token balances.
- Compute both sides of the identity before and after. If they still agree, output no vulnerability.
- Check whether `min-out` / `min-shares` / `min-underlying` slippage bounds, caps, pause states, health checks, `check-impl-auth` / `check-caller-auth`, or Clarity's own overflow aborts already prevent the divergence.
- Quantify the divergence per call and say whether it is repeatable, and who absorbs it.
- Require exact file/function support and a reproducible Clarinet / vitest simnet PoC that asserts the numbers.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[The broken identity as an equation, the code path, root cause, attacker call arguments, exploit flow, and why existing guards fail]

### Impact Explanation
[Divergence per call, repeatability, total extractable or frozen value, party bearing the loss, matching Immunefi severity category]

### Likelihood Explanation
[Preconditions, capital cost to the attacker, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Clarinet simnet test plan with the exact numeric assertions on both sides of the identity]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for Zest v2 conservation claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- A conservation claim is only valid if the report states the broken identity as an equation and shows both sides numerically. Reject prose-only claims.
- Reject anything requiring a DAO signer, executor, market impl, authorized contract, miner, oracle publisher, node operator, or leaked keys.
- OUT OF SCOPE, reject on sight: any flashloan logic (`flashloan`, its fee, its permission whitelist, `in-flashloan`) - though a flashloan used purely as capital for a different attack is fine; liquidation of disabled collateral and other deliberate safety design decisions; anything requiring DAO compromise or an accidental or incorrect DAO registry update, since full DAO control of the asset and egroup registries is intended design and egroup invariants needing global position knowledge are verified off-chain before approval.
- Also reject: leaked keys, privileged addresses, external stablecoin depegs the attacker did not cause through a bug here, 51% / basic economic / governance attacks, Sybil, centralization risk, lack of liquidity, incorrect data supplied by third-party oracles, best-practice notes, feature requests, and test or configuration files. Oracle manipulation caused by a bug in THIS code stays in scope.
- The impact must be one of: Critical - direct theft of user funds at rest or in motion other than unclaimed yield, permanent freezing of funds, or protocol insolvency; High - theft of unclaimed yield or royalties, permanent freezing of unclaimed yield or royalties, or temporary freezing of funds.
- Reject governance-parameter, centralization, Sybil, 51%, lack-of-liquidity, external-stablecoin-depeg and best-practice claims. Oracle manipulation and flashloan attacks are NOT excluded when the attacker causes them through a bug in this code.
- Reject Pyth/Wormhole internals, third-party contracts, `local-testing/**`, tests, mocks, deployment plans, `.toml`, docs, read-only aggregator and dependency-only findings.
- Reject if the bug was already fixed, acknowledged, or covered by the published Clarity Alliance, Greybeard or Asymmetric audits.
- Reject a divergence of a single indivisible unit that is not repeatable and cannot be amplified.
- A valid report must be triggerable by an ordinary Stacks principal on the currently deployed mainnet contracts.
- The final impact must map to an in-scope Immunefi category: direct theft or permanent freezing of funds, theft or freezing of unclaimed yield, protocol insolvency, or temporary freezing of funds.
- A PoC is mandatory. Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. The conservation identity written explicitly, with both sides evaluated before and after.
3. Clear root cause: which write, which rounding, or which missing reconciliation causes the divergence.
4. Reachable exploit path: preconditions -> attacker call -> trigger -> measured divergence.
5. Slippage bounds, caps, pause states, health checks, auth guards and Clarity overflow aborts reviewed and shown insufficient.
6. Divergence quantified per call, shown repeatable or amplifiable, and the losing party named.
7. Reproducible proof: Clarinet / vitest simnet test asserting the numbers.

## Silent Triage Questions
Before output, internally answer:
- What exactly is the equation, and does it actually fail?
- Can an ordinary funded principal trigger it without any privileged role?
- Is the divergence caused by this code, not by an oracle, a third-party token, or a governance choice?
- How much value moves per call, and can it be repeated?
- Would an Immunefi triager accept the arithmetic?
- What exact test would prove it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the broken identity and impact]

## Finding Description
[Exact code path, the equation, root cause, exploit flow, and why existing guards fail]

## Impact Explanation
[Quantified divergence, repeatability, party bearing the loss, Immunefi category]

## Likelihood Explanation
[Attacker capability, preconditions, capital cost, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or Clarinet simnet test plan with numeric assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project conservation analog scan prompt for Zest v2.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production repo context only (`mainnet/contracts/**`). Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-principal analogs that break a value identity: share minting and burning versus backing, the per-user debt ledger versus the vault aggregate, custody versus the collateral map, interest created versus interest distributed, fees charged versus fees forwarded, rounding direction across paired conversions, or decimal normalization losing value.
- OUT OF SCOPE, reject on sight: any flashloan logic (`flashloan`, its fee, its permission whitelist, `in-flashloan`) - though a flashloan used purely as capital for a different attack is fine; liquidation of disabled collateral and other deliberate safety design decisions; anything requiring DAO compromise or an accidental or incorrect DAO registry update, since full DAO control of the asset and egroup registries is intended design and egroup invariants needing global position knowledge are verified off-chain before approval.
- Also reject: leaked keys, privileged addresses, external stablecoin depegs the attacker did not cause through a bug here, 51% / basic economic / governance attacks, Sybil, centralization risk, lack of liquidity, incorrect data supplied by third-party oracles, best-practice notes, feature requests, and test or configuration files. Oracle manipulation caused by a bug in THIS code stays in scope.
- The impact must be one of: Critical - direct theft of user funds at rest or in motion other than unclaimed yield, permanent freezing of funds, or protocol insolvency; High - theft of unclaimed yield or royalties, permanent freezing of unclaimed yield or royalties, or temporary freezing of funds.
- Reject malicious-miner, chain-reorg, MEV-only, privileged-address, oracle-publisher, third-party token, `local-testing/**`, mock, deployment-plan, dependency-only and no-impact analogs.

## Validate
- Map the bug class to the strongest reachable Zest path and state the identity it would break as an equation.
- Evaluate both sides before and after the attacker's call sequence.
- Prove root cause with exact file/function support.
- Accept only concrete protocol insolvency, theft of principal or unclaimed yield, permanent freezing of funds, or value minted from nothing.

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
