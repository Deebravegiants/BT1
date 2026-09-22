import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 10
# todo: the path from https://github.com/GuardianOrg/alt-fun-defender-contest-guardian
SOURCE_REPO = "GuardianOrg/alt-fun-defender-contest-guardian"
# todo: the name of the repository
REPO_NAME = "alt-fun-defender-contest-guardian"
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
    # Lifecycle core: launch, curve buy/sell, graduation triggers, two-phase graduation,
    # HyperSwap V2 LP seeding and rebalancing, launch-delay gate, router allowlist
    # =================================================================================
    "packages/contracts/src/Bonding.sol",

    # =================================================================================
    # User entry point: USDC in/out, LT mint/redeem, fee layer, refunds, permit paths
    # =================================================================================
    "packages/contracts/src/Zap.sol",

    # =================================================================================
    # Bonding-curve AMM math: buy/sell quoting, overflow cap, graduation LT drain
    # =================================================================================
    "packages/contracts/src/Router.sol",

    # =================================================================================
    # Per-token curve pair: stored reserves, K invariant, asset/token transfers
    # =================================================================================
    "packages/contracts/src/Pair.sol",

    # =================================================================================
    # Pair registry and one-shot router wiring consumed by Router and Bonding
    # =================================================================================
    "packages/contracts/src/Factory.sol",

    # =================================================================================
    # Launched ERC20 clone: fixed supply, owner-only burn-from-any, EIP-2612 permit
    # =================================================================================
    "packages/contracts/src/Token.sol",

    # =================================================================================
    # Fee custody and accounting: accrual solvency, creator and protocol claims, sweeps
    # =================================================================================
    "packages/contracts/src/FeeVault.sol",

    # =================================================================================
    # Graduated LP custody: one-shot lock recording gating finalizeGraduation
    # =================================================================================
    "packages/contracts/src/LPLock.sol",

    # =================================================================================
    # External integration surfaces the protocol trusts: BounceTech LT and registry,
    # curve pair/router ABIs, and the HyperSwap V2 factory/pair/router ABIs
    # =================================================================================
    "packages/contracts/src/interfaces/IBounceLeveragedToken.sol",
    "packages/contracts/src/interfaces/IBounceFactory.sol",
    "packages/contracts/src/interfaces/IBounceGlobalStorage.sol",
    "packages/contracts/src/interfaces/IPair.sol",
    "packages/contracts/src/interfaces/IRouter.sol",
    "packages/contracts/src/interfaces/IZap.sol",
    "packages/contracts/src/interfaces/IUniswapV2Factory.sol",
    "packages/contracts/src/interfaces/IUniswapV2Pair.sol",
    "packages/contracts/src/interfaces/IUniswapV2Router02.sol",
]


target_scopes = [
    "Critical. An attacker hijacks graduation LP seeding by pre-creating or pre-skewing the HyperSwap V2 TOKEN/LT pair before anyone calls Bonding.finalizeGraduation: Bonding._ensureUniswapV2Pair, _seedUniswapV2Direct (its skim and totalSupply == 0 branch), _seedRebalancing with its DIRECT_MINT_PRESEED_BPS dust threshold, _pairRebalance, _noFeeSwapInput, _swapBudget and _routerDepositAndDispose, which calls IUniswapV2Router02.addLiquidity with amountAMin = amountBMin = 1 and block.timestamp as deadline, let the attacker choose the pool price that Bonding must swap its whole curve-raised LT and lpReserve inventory into, so the graduated pool opens away from the last curve price and the attacker back-runs the seed to take the LT and tokens that should have gone to LPLock.",
    "Critical. An attacker steals the LT and launched tokens held by Bonding between the two graduation phases: Bonding.triggerGraduation and finalizeGraduation are both permissionless with no deadline, _enterGraduating drains the entire real LT reserve out of the curve Pair via Router.graduate into Bonding, and finalizeGraduation recomputes protectedLT as balanceOf(Bonding) - pendingGraduation.ltFromPair before _seedUniswapV2Direct and _sweepLTToOwner, so an attacker who controls the gap - by donating LT, by timing a second token that shares the same ltAddress into Graduating first, or by choosing the block in which finalize runs - makes protectedLT, _ltSwapInventory or the swept amount misattribute another token's escrowed LT and walks off with curve proceeds.",
    "Critical. An attacker permanently freezes every holder of a token by forcing Bonding.finalizeGraduation to revert forever while the lifecycle is stuck at Lifecycle.Graduating: Bonding.buy, Bonding.sell, Zap._buyInternal and Zap._sellInternal all revert with TokenIsGraduating in that state, so any reachable revert inside finalizeGraduation - IUniswapV2Pair.mint returning zero or reverting on INSUFFICIENT_LIQUIDITY_MINTED in _seedDirectMint, LPLock.recordLock reverting with ZeroAmount when _routerDepositAndDispose returns liquidity == 0 or with AlreadyLocked, an underflow in _seedRebalancing's reserve arithmetic, or a transfer of tokensForLP / ltFromPair larger than Bonding's real balance - leaves the curve drained, the tokens unsellable and the LP unmintable with no permissionless recovery path.",
    "Critical. An attacker extracts curve reserves or bricks a live curve through rounding and the K check: Pair.swap accepts (newTokenReserve + 1) * (newAssetReserve + 1) >= _pool.k, Router._computeBuy floors k / newReserveAsset in the buyer's favour and ceils only on the overflow-capped branch, Router._computeSell floors k / newReserveToken in the seller's favour, and neither side charges a curve fee, so repeated buy/sell round trips through Zap can return more LT than was paid in, shrink the stored assetReserve below _launchTimeVirtualLtReserve so Bonding.canGraduate and previewLtUntilGraduation underflow and every later buy and sell reverts, or let Router.sell ask Pair.transferAsset for more LT than the pair actually holds.",
    "Critical. An attacker drains the USDC and LT that Zap is holding mid-flow, or escapes the fee entirely, through the buy refund and pro-rata fee accounting: Zap._executeBuy's floor-bump branch, its baseToLtAmount / ltToBaseAmount pre-sizing against Bonding.previewLtUntilGraduation, effectiveBaseSpent = (amountInUsed * baseToConvert) / ltMinted, the Math.mulDiv Ceil fee capped at feeOnGross, and the three payouts to msg.sender (tokensOut, ltExcess, usdcLeft plus feeRefund) let a crafted usdcAmount near the graduation cap or the BounceTech mint floor refund more USDC or LT than the caller supplied, or mint LT through Zap at zero effective fee at other users' expense.",
    "Critical. An attacker manipulates the graduation trigger to graduate a token at a price of their choosing or to block graduation forever: Bonding.canGraduate, previewLtUntilGraduation, _launchTimeVirtualLtReserve (IPair.k() / Token.TOTAL_SUPPLY()), the IPair.tokenBalance() == 0 supply trigger, and _prepareGraduationLiquidity's tokensForLP = (ltFromPair * tokenReserve) / assetReserve with its LP_RESERVE cap let a direct ERC20 donation of the launched token or the LT to the curve Pair, a self-crafted final buy, or a stale IBounceLeveragedToken.exchangeRate read fix ltFromPair, tokensForLP and lpBurned at values that hand the attacker the difference or leave LP_RESERVE tokens unburnable.",
    "Critical. An attacker steals value on the post-graduation path in Zap: _swapOnUniswapV2 resolves the pool by Bonding.graduatedPair(tokenIn) with a silent fallback to graduatedPair(tokenOut), never checks that pair is non-zero or that token0/token1 are the expected TOKEN and LT, quotes with IUniswapV2Pair.getAmountOut and then transfers and calls swap direct-to-pair with no deadline, while _buyOnUniswapV2 and _sellOnUniswapV2 rely solely on Zap's outer minTokensOut / minUsdcOut - so a mis-resolved pair, a zero-address pair, or a buy routed with minTokensOut = 0 lets an attacker take the trader's USDC-derived LT or the tokens Zap is holding.",
    "High. An attacker steals accrued protocol or creator fees, or makes the vault insolvent for honest creators: FeeVault.accrue's balance check against totalAccruedCreator + protocolBalance, claim, claimProtocol and the permissionless sweepDonations, combined with Zap._accrueFee's creatorShare / protocolShare split and its creatorOf(tokenAddress) lookup and Bonding.transferCreator, let an attacker who launches a token and re-points its creator, or who times a claim against a sweep or an accrual, withdraw USDC credited to another creator or to feeTo, or strand balances that can never be claimed.",
    "Critical. An attacker hijacks or corrupts a token launch so the curve opens on terms they control: Bonding.launch, _mixSalt, predictTokenAddress, _checkVanity with VANITY_TRAILING_ZEROS, _storeTokenInfo writing tokenInfo before _deployAndSeed, _deployAndSeed's virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate with its uint112 ceiling and Router.addInitialLiquidity (totalSupply as the virtual reserve against curveSupply real tokens), Factory.createPair's ltFor / pairFor registry, and the LAUNCH_TRADING_DELAY_BLOCKS gate implemented as the transient _SEED_BUY_BYPASS_SLOT consumed by _enforceLaunchDelay, let an unprivileged caller seed a curve at a K that misprices the pool, reuse or clear the bypass slot to buy inside the delay window, or bind a token to a pair or LT other than the one recorded in tokenInfo.",
    "Critical/High blind spot. An ordinary trader, token creator or unrelated wallet abuses an assumption alt.fun never wrote down: a value read again after the check that authorised it (lifecycle, pair reserves, tokenBalance, exchangeRate, creatorOf) inside one Zap call, a guard present on the curve path but missing on the graduated path or on the permit twin (buyWithPermit, sellWithPermit, createTokenWithPermit), state left inconsistent when Zap.sell short-circuits into triggerGraduation and returns 0, LT or launched tokens stranded on Zap, Bonding or the curve Pair that anyone can sweep, an external BounceTech LT whose exchangeRate, minTransactionSize, mint pause or ltExists flag moves between two reads in the same transaction, a second token sharing one ltAddress interfering with the first token's escrow, the first or last trade on a curve taking a rounding edge the formula only proved safe mid-curve, or a HyperSwap V2 pool whose token0 ordering, fee or pre-existing reserves differ from what the seeding code assumes - yielding theft of trader, creator or LP funds, a permanently frozen token, an LP seeded away from the curve close price, or protocol insolvency.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one alt.fun target.

    ```
    target_file format:
    "'File Name: packages/contracts/src/Bonding.sol -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit questions for this exact alt.fun target:

    {target_file}

    Project focus:
    alt.fun is a token launchpad on HyperEVM. Each launched Token (1B supply, 75% on the curve, 25% held in Bonding as lpReserve) trades on an internal constant-product curve Pair whose reserve asset is an external BounceTech Leveraged Token (LT). Users only ever touch USDC: Zap pulls USDC, skims a fee into FeeVault, mints LT, and routes through Bonding/Router on the curve or direct-to-pair on HyperSwap V2 after graduation. Graduation is two-phase: _enterGraduating drains the curve's real LT and precomputes tokensForLP/lpBurned, then the permissionless finalizeGraduation seeds a HyperSwap V2 TOKEN/LT pool and locks the LP in LPLock.

    Rules:
    * Treat `File Name:` as the exact file/contract.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Solidity symbols (contract, function, modifier, struct, enum, event, error, constant or storage field) when possible.
    * Attacker is unprivileged only: any funded EOA or contract that calls Zap.createToken/createTokenWithPermit, buy/buyWithPermit, sell/sellWithPermit, Bonding.triggerGraduation, Bonding.finalizeGraduation, Bonding.transferCreator on a token they launched, FeeVault.claim/claimProtocol/sweepDonations, LPLock and Pair views, that ERC20-transfers tokens or LT directly to any contract, and that can create or seed a HyperSwap V2 pair themselves.
    * Attacker is NOT the Bonding/Zap/FeeVault/LPLock owner, not on Bonding's router allowlist or FeeVault's depositor allowlist, not a BONDING_ROLE or DEFAULT_ADMIN_ROLE holder, not an LPLock locker, not a BounceTech operator or the HyperSwap deployer, and holds no other user's key. Never assume a malicious admin, upgrade, leaked key, or social engineering.
    * Out of scope, never ask about: the web app, API, indexer, telegram bot, shared/config packages, deploy scripts, HyperEVM client or consensus bugs, a malicious validator or sequencer, the internals of BounceTech LT or HyperSwap V2 themselves, RPC, off-chain monitoring, dependency versions, centralization or governance risk, and pure MEV ordering with no protocol bug.
    * Ignore test files, mocks, deployment scripts, docs, lib/ dependencies, and config-only findings.
    * Every question must describe a real transaction the attacker actually submits: named external function, the exact arguments, the token/LT/pair state they rely on, and any tokens they pre-transferred. No generic unbounded-loop, gas-exhaustion, memory-growth or "what if the input is huge" speculation without a concrete payload and a concrete broken invariant.
    * Generate 40 to 80 high-signal questions.
    * At least 70% must target theft of trader, creator or LP funds, permanent freezing of a token or its curve, LP seeded away from the curve close price, or protocol insolvency.
    * Every question must be testable by a `forge test` unit or fuzz test against the contracts in packages/contracts/src.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Curve soundness: after every Pair.swap the constant product never decreases against the pool, and no buy/sell round trip returns more LT or more tokens than it put in.
    * Reserve backing: the curve Pair's stored assetReserve never falls below _launchTimeVirtualLtReserve, and tokens and LT paid out never exceed what the pair or Bonding actually holds for that token.
    * Graduation integrity: ltFromPair is exactly the real LT raised by that curve, tokensInLP + lpBurned == LP_RESERVE, the seeded pool opens at the last curve price, and the LP lands in LPLock.
    * Liveness: no user-submitted transaction can leave a token permanently in Lifecycle.Graduating or otherwise make buy, sell and finalizeGraduation revert forever.
    * Fee solvency: FeeVault's USDC balance always covers totalAccruedCreator + protocolBalance, and fees are attributed to the creator recorded at accrual time.

    Each question must include:
    1. target function/method;
    2. attacker action (a concrete call: function, arguments, value);
    3. preconditions (wallet funding, token lifecycle, pair reserves, pre-transferred tokens or LT, pre-created V2 pair);
    4. execution sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger EXECUTION_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: forge test PARAMETERS and assert CURVE_SOUNDNESS, RESERVE_BACKING, GRADUATION_INTEGRITY, LIVENESS, or FEE_SOLVENCY.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused alt.fun exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: any funded address that calls Zap (createToken, buy, sell and their permit variants), Bonding's permissionless functions (triggerGraduation, finalizeGraduation, transferCreator on a token it launched), FeeVault (claim, claimProtocol, sweepDonations), that ERC20-transfers tokens or LT directly to any contract, and that can create or seed a HyperSwap V2 pair itself. No owner, no router-allowlist or depositor-allowlist member, no BONDING_ROLE/DEFAULT_ADMIN_ROLE, no LPLock locker, no BounceTech operator, no other user's key.
- Reject privileged-caller, upgrade, leaked-key, malicious-validator, off-chain, RPC, indexer, API, web, telegram-bot, deploy-script and misconfiguration-only paths.
- Reject bugs inside BounceTech LT or HyperSwap V2 themselves, HyperEVM client/consensus bugs, centralization and governance claims, pure MEV ordering with no protocol bug, best-practice critiques, and test/mock/docs/lib/config-only findings.
- Reject generic gas-exhaustion or unbounded-loop claims with no concrete call payload and no broken invariant.
- Focus on real on-chain impact: theft of trader, creator or LP funds, permanent freezing of a token or its curve, an LP pool seeded away from the curve close price, unbacked token or LT payouts, or FeeVault insolvency.

## Validate
- Trace the exact reachable path from the attacker's transaction into the affected function, with the arguments and pre-state they supply.
- Check whether existing guards already stop it: Zap's nonReentrant and minTokensOut/minUsdcOut, Bonding's onlyRouter router allowlist, nonReentrant and Lifecycle gates, _enforceLaunchDelay, Router's BONDING_ROLE, Pair's onlyRouter and K check, Factory's one-shot setRouter, FeeVault's onlyDepositor and UnderfundedAccrual check, LPLock's AlreadyLocked one-shot, Solidity 0.8 checked arithmetic, and the graduation preconditions in canGraduate / previewLtUntilGraduation.
- Confirm the path is reachable on the deployed configuration described in docs/contracts-scope.md and packages/contracts/AGENTS.md (HyperEVM, USDC 6dp, HyperSwap V2, a live BounceTech LT).
- Accept only concrete fund loss or freezing, a mis-seeded LP, unbacked payouts, or FeeVault insolvency.
- Require exact file/function support and a reproducible `forge test` PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker call and arguments, exploit flow, and why existing guards fail]

### Impact Explanation
[Concrete scoped impact and severity: Critical (direct theft of user, creator or LP funds, permanent freezing of funds, protocol insolvency) or High (theft of accrued fees or LP value, temporary freezing of funds)]

### Likelihood Explanation
[Preconditions, funding, token lifecycle and pair state needed, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[forge test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for alt.fun.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production contract context only (packages/contracts/src). Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof. The analog must stand on alt.fun's own code.
- Keep only analogs an unprivileged trader, token creator or unrelated wallet can reach: Zap.createToken/buy/sell and their permit variants, Bonding.triggerGraduation / finalizeGraduation / transferCreator, FeeVault.claim / claimProtocol / sweepDonations, direct ERC20 transfers of a launched Token or an LT into Pair, Bonding, Zap or FeeVault, and pre-creating or pre-seeding the HyperSwap V2 TOKEN/LT pair before graduation.
- Map the class onto alt.fun's real shape, which is where its bugs live:
  * bonding-curve AMM math with a virtual token reserve and no curve fee (Router._computeBuy / _computeSell, Pair.swap's `+1` K slack, the overflow cap and its ceil-rounded amountInUsed);
  * a reserve asset that is an external rebasing-priced LT read live via exchangeRate / baseToLtAmount / ltToBaseAmount / minTransactionSize;
  * USDC-to-LT-to-token layering in Zap with pro-rata fees, an LT overshoot refund and a USDC refund in the same call;
  * dual graduation triggers (USD value and tokenBalance() == 0) computed from stored reserves plus a recovered virtual reserve;
  * a permissionless two-phase graduation that parks all curve-raised LT and 250M tokens on Bonding between phases;
  * LP seeding into an attacker-influenceable HyperSwap V2 pair, including addLiquidity with amountMin = 1 and the _seedRebalancing / _pairRebalance / _seedDirectMint fallbacks;
  * a one-shot LPLock.recordLock that finalizeGraduation cannot skip.
- Reject privileged-caller, upgrade, leaked-key, malicious-validator, off-chain, RPC, web/API/indexer/bot, deploy-script, dependency-only, mocked-only paths, bugs inside BounceTech LT or HyperSwap V2 themselves, and no-impact analogs.
- Medium, High and Critical only; no low, informational, best-practice or gas-only analogs.

## Validate
- Map the bug class to the strongest reachable path from transactions a single unprivileged address can submit, naming the exact functions and arguments.
- Prove root cause with exact file/function support in packages/contracts/src.
- Accept only concrete theft or permanent freezing of trader, creator or LP funds, an LP seeded away from the curve close price, unbacked token or LT payouts, or FeeVault insolvency.

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
    Generate a strict bounty-style validation prompt for alt.fun security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and RESEARCHER.md for scope, exclusions, and valid impact classes.
- Scope is the on-chain contracts only: packages/contracts/src/Bonding.sol, Zap.sol, Router.sol, Pair.sol, Factory.sol, Token.sol, FeeVault.sol, LPLock.sol and packages/contracts/src/interfaces/. The web app, API, indexer, telegram bot, shared/config packages, deploy scripts, tests, mocks and lib/ dependencies are out of scope.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Critical, High and Medium are in scope as the Immunefi V2.3 smart-contract scale defines them. Reject Low, informational and best-practice findings.
- Reject malicious-owner, upgrade-based, leaked-key, allowlisted-router, FeeVault-depositor, BONDING_ROLE, DEFAULT_ADMIN_ROLE, LPLock-locker, BounceTech-operator, malicious-validator, off-chain, RPC, web/API/indexer/bot, monitoring, deployment, dependency-only, docs/style and test/mock/config-only issues.
- Reject if the exploit needs anything beyond what an unprivileged address can do: call Zap's public entry points, call Bonding.triggerGraduation / finalizeGraduation / transferCreator on its own token, call FeeVault's permissionless functions, ERC20-transfer tokens or LT into a contract, or create and seed a HyperSwap V2 pair.
- Reject bugs inside BounceTech LT or HyperSwap V2 themselves, HyperEVM client or consensus bugs, centralization and governance claims, lack of liquidity, and pure MEV ordering with no protocol bug.
- Treat these as documented and accepted, not findings on their own: the uncapped seed buy, the buy-only LAUNCH_TRADING_DELAY_BLOCKS gate, atomic-redeem-only sells reverting on LT idle-buffer depletion, BounceTech mint pauses DoSing buys while sells work, LT donated to the curve Pair staying locked there, retired LTs freezing the USD graduation trigger, and exchange-rate drift on the rate-only graduation path. A report is only valid if it shows an impact beyond the documented behaviour.
- Reject if the bug was already fixed, acknowledged or publicly disclosed, per the eligibility rules.
- The final impact must map to an in-scope category: Critical - direct theft of trader, creator or LP funds, permanent freezing of funds or of a token stuck in Lifecycle.Graduating, unbacked token or LT payouts, or protocol insolvency; High - theft of accrued fees or of LP value through a mis-seeded graduation pool, or temporary freezing of funds; Medium - a contract unable to operate from lack of funds, unprofitable griefing, or theft of gas.
- A PoC is mandatory: prose alone is not accepted. Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and a broken curve-soundness, reserve-backing, graduation-integrity, liveness or fee-solvency invariant.
3. Reachable exploit path: preconditions (funding, token lifecycle, pair reserves, pre-transferred tokens or LT, pre-created V2 pair) -> submitted call with its arguments -> trigger -> bad result.
4. Existing guards reviewed and shown insufficient: Zap's nonReentrant and slippage bounds, Bonding's onlyRouter allowlist, nonReentrant, Lifecycle gates and _enforceLaunchDelay, Router's BONDING_ROLE, Pair's onlyRouter and K check, Factory's one-shot setRouter, FeeVault's onlyDepositor and UnderfundedAccrual check, LPLock's one-shot AlreadyLocked, and Solidity 0.8 checked arithmetic.
5. Concrete in-scope Critical/High (or clearly argued Medium) impact with realistic likelihood.
6. Reproducible proof path: a `forge test` unit or fuzz PoC against packages/contracts/src.
7. No obvious rejection reason from SECURITY.md, the documented accepted tradeoffs above, privilege assumptions, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can an ordinary address trigger this with the public calls listed above, holding no role and no other user's key?
- Does the code actually behave as claimed on the deployed HyperEVM configuration (USDC 6dp, HyperSwap V2, a live BounceTech LT)?
- Is the impact caused by alt.fun's own contracts, not by BounceTech, HyperSwap, the chain, or a privileged actor?
- Is it beyond the tradeoffs already documented in docs/contracts-scope.md and packages/contracts/AGENTS.md?
- Is the loss, freeze, mis-seeded LP or insolvency concrete rather than hypothetical?
- Would a triager accept the proof-of-concept, and what exact test proves it?

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
[Concrete in-scope impact, severity rationale, and Immunefi V2.3 category]

## Likelihood Explanation
[Attacker capability, funding and token/pair state required, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or a forge test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt
