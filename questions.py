import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the path from https:///github.com/dfinity/ICRC-1
SOURCE_REPO = "Kelp-DAO/LRT-rsETH"
# todo: the name of the repository
REPO_NAME = "LRT-rsETH"
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
    'contracts/FeeReceiver.sol',
    'contracts/KERNEL/KERNEL.sol',
    'contracts/KERNEL/KernelDepositPool.sol',
    'contracts/KERNEL/KernelMerkleDistributor.sol',
    'contracts/KERNEL/KernelReceiver.sol',
    'contracts/KERNEL/KernelTop100MerkleDistributor.sol',
    'contracts/KERNEL/KernelVaultETH.sol',
    'contracts/L1Vault.sol',
    'contracts/L1VaultV2.sol',
    'contracts/L2/RsETHTokenWrapper.sol',
    'contracts/LRTConfig.sol',
    'contracts/LRTConverter.sol',
    'contracts/LRTDepositPool.sol',
    'contracts/LRTOracle.sol',
    'contracts/LRTUnstakingVault.sol',
    'contracts/LRTWithdrawalManager.sol',
    'contracts/NodeDelegator.sol',
    'contracts/NodeDelegatorHelper.sol',
    'contracts/PubkeyRegistry.sol',
    'contracts/RSETH.sol',
    'contracts/agETH/AGETHMultiChainRateProvider.sol',
    'contracts/agETH/AGETHPoolV3.sol',
    'contracts/agETH/AGETHRateReceiver.sol',
    'contracts/agETH/AGETHTokenWrapper.sol',
    'contracts/bridges/ArbitrumLidoBridge.sol',
    'contracts/bridges/ArbitrumMessenger.sol',
    'contracts/bridges/BaseMessenger.sol',
    'contracts/bridges/LidoBridge.sol',
    'contracts/bridges/LineaMessenger.sol',
    'contracts/bridges/OptimismMessenger.sol',
    'contracts/bridges/ScrollMessenger.sol',
    'contracts/bridges/SonicBridgeReceiver.sol',
    'contracts/bridges/SonicChainNativeTokenBridge.sol',
    'contracts/bridges/TACWETHBridge.sol',
    'contracts/bridges/UnichainMessenger.sol',
    'contracts/ccip/ConfirmedOwnerWithProposal.sol',
    'contracts/ccip/ERC677.sol',
    'contracts/ccip/IBurnMintERC20.sol',
    'contracts/ccip/WrappedRSETH.sol',
    'contracts/cross-chain/CrossChainRateProvider.sol',
    'contracts/cross-chain/CrossChainRateReceiver.sol',
    'contracts/cross-chain/MultiChainRateProvider.sol',
    'contracts/cross-chain/RSETHMultiChainRateProvider.sol',
    'contracts/cross-chain/RSETHRateProvider.sol',
    'contracts/cross-chain/RSETHRateReceiver.sol',
    'contracts/external/arbitrum/IArbitrumL2GatewayRouter.sol',
    'contracts/external/chainlink/IRouterClient.sol',
    'contracts/external/chainlink/libraries/Client.sol',
    'contracts/external/eigenlayer/interfaces/IAVSRegistrar.sol',
    'contracts/external/eigenlayer/interfaces/IAllocationManager.sol',
    'contracts/external/eigenlayer/interfaces/IDelegationManager.sol',
    'contracts/external/eigenlayer/interfaces/IETHPOSDeposit.sol',
    'contracts/external/eigenlayer/interfaces/IEigenPod.sol',
    'contracts/external/eigenlayer/interfaces/IEigenPodManager.sol',
    'contracts/external/eigenlayer/interfaces/IPausable.sol',
    'contracts/external/eigenlayer/interfaces/IPauserRegistry.sol',
    'contracts/external/eigenlayer/interfaces/IRewardsCoordinator.sol',
    'contracts/external/eigenlayer/interfaces/IShareManager.sol',
    'contracts/external/eigenlayer/interfaces/ISignatureUtils.sol',
    'contracts/external/eigenlayer/interfaces/IStrategy.sol',
    'contracts/external/eigenlayer/interfaces/IStrategyManager.sol',
    'contracts/external/eigenlayer/libraries/BeaconChainProofs.sol',
    'contracts/external/eigenlayer/libraries/Endian.sol',
    'contracts/external/eigenlayer/libraries/Merkle.sol',
    'contracts/external/eigenlayer/libraries/OperatorSetLib.sol',
    'contracts/external/eigenlayer/libraries/SlashingLib.sol',
    'contracts/external/layerzero/interfaces/ILayerZeroEndpoint.sol',
    'contracts/external/layerzero/interfaces/ILayerZeroReceiver.sol',
    'contracts/external/layerzero/interfaces/ILayerZeroUserApplicationConfig.sol',
    'contracts/external/layerzero/interfaces/IOFT.sol',
    'contracts/external/layerzero/interfaces/IStargatePoolNative.sol',
    'contracts/external/lido/IL2ERC20Bridge.sol',
    'contracts/external/lido/ILido.sol',
    'contracts/external/lido/IWstETH.sol',
    'contracts/external/weth/IWETH.sol',
    'contracts/interfaces/IFeeReceiver.sol',
    'contracts/interfaces/IKERNEL_OFTAdapter.sol',
    'contracts/interfaces/ILRTConfig.sol',
    'contracts/interfaces/ILRTConverter.sol',
    'contracts/interfaces/ILRTDepositPool.sol',
    'contracts/interfaces/ILRTOracle.sol',
    'contracts/interfaces/ILRTUnstakingVault.sol',
    'contracts/interfaces/ILRTWithdrawalManager.sol',
    'contracts/interfaces/INodeDelegator.sol',
    'contracts/interfaces/IPriceFetcher.sol',
    'contracts/interfaces/IPubkeyRegistry.sol',
    'contracts/interfaces/IRSETH.sol',
    'contracts/interfaces/IRSETH_OFTAdapter.sol',
    'contracts/interfaces/L2/IArbitrumMessenger.sol',
    'contracts/interfaces/L2/IBaseMessenger.sol',
    'contracts/interfaces/L2/IL2Messenger.sol',
    'contracts/interfaces/L2/IL2TokenBridge.sol',
    'contracts/interfaces/L2/ILineaMessageService.sol',
    'contracts/interfaces/L2/IOptimismMessenger.sol',
    'contracts/interfaces/L2/IScrollMessenger.sol',
    'contracts/interfaces/L2/ISonicBridge.sol',
    'contracts/interfaces/L2/IUnichainMessenger.sol',
    'contracts/interfaces/aave/IAToken.sol',
    'contracts/interfaces/aave/IPool.sol',
    'contracts/interfaces/aave/IPoolDataProvider.sol',
    'contracts/interfaces/aave/IWrappedTokenGatewayV3.sol',
    'contracts/king-protocol/IKingProtocol.sol',
    'contracts/king-protocol/TokenSwap.sol',
    'contracts/offchain/OffchainConfig.sol',
    'contracts/oracles/ChainlinkPriceOracle.sol',
    'contracts/oracles/EthXPriceOracle.sol',
    'contracts/oracles/OneETHPriceOracle.sol',
    'contracts/oracles/RETHPriceOracle.sol',
    'contracts/oracles/RSETHPriceFeed.sol',
    'contracts/oracles/SfrxETHPriceOracle.sol',
    'contracts/oracles/SwETHPriceOracle.sol',
    'contracts/pools/RSETHPool.sol',
    'contracts/pools/RSETHPoolNoWrapper.sol',
    'contracts/pools/RSETHPoolV2.sol',
    'contracts/pools/RSETHPoolV2ExternalBridge.sol',
    'contracts/pools/RSETHPoolV2NBA.sol',
    'contracts/pools/RSETHPoolV3.sol',
    'contracts/pools/RSETHPoolV3ExternalBridge.sol',
    'contracts/pools/RSETHPoolV3WithNativeChainBridge.sol',
    'contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol',
    'contracts/pools/oracle/InterimRSETHOracle.sol',
    'contracts/pools/oracle/WETHOracle.sol',
    'contracts/unstaking-adapters/UnstakeStETH.sol',
    'contracts/unstaking-adapters/UnstakeSwETH.sol',
    'contracts/utils/Bytes32AddressLib.sol',
    'contracts/utils/CREATE3.sol',
    'contracts/utils/CREATE3Factory.sol',
    'contracts/utils/DoubleEndedQueue.sol',
    'contracts/utils/HashStorage.sol',
    'contracts/utils/LRTConfigRoleChecker.sol',
    'contracts/utils/LRTConstants.sol',
    'contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol',
    'contracts/utils/MerkleDistributor/MerkleDistributor.sol',
    'contracts/utils/Recoverable.sol',
    'contracts/utils/UnlockedWithdrawalsInitializer.sol',
    'contracts/utils/UtilLib.sol',
    'contracts/utils/WadMath.sol',
]
target_scopes = [
    'Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield',
    'Critical. Permanent freezing of funds',
    'Critical. Protocol insolvency',
    'High. Theft of unclaimed yield',
    'Medium. Unbounded gas consumption',
    'Medium. Permanent freezing of unclaimed yield',
    'Medium. Temporary freezing of funds',
    "Low. Contract fails to deliver promised returns, but doesn't lose value",
    'Low. Block stuffing',
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one LRT-rsETH target.

    target_file format:
    "'File Name: contracts/LRTDepositPool.sol -> Scope: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit and fuzzing questions for this exact LRT-rsETH target:

    {target_file}

    Use live context from the project if available: LRTConfig, RSETH, LRTDepositPool, NodeDelegator, LRTWithdrawalManager, LRTUnstakingVault, L1Vault/V2, FeeReceiver, LRTOracle, price oracles, rsETH pools, token wrappers, KERNEL/agETH pools and vaults, bridge/messenger contracts, rate providers/receivers, Merkle distributors, access-control roles, pausing, config updates, external EigenLayer/Lido/Aave/WETH integrations, and ERC20 mint/burn/accounting flows.

    Protocol focus:
    Kelp DAO LRT-rsETH is a liquid restaking protocol. Users deposit ETH or LST collateral, receive rsETH or related wrapper/pool shares, assets are delegated/restaked or bridged, and withdrawals, yield, fees, rates, and claims are settled through production contracts in this repository only.

    Core invariants:

    * User funds, protocol collateral, withdrawals, vault assets, bridged assets, and pool reserves must never be stolen, lost, made insolvent, or permanently frozen.
    * rsETH, wrapper, pool-share, and KERNEL/agETH mint/burn/accounting must remain fully backed by the assets and rates they represent.
    * Deposits, withdrawals, unstaking, claims, fee collection, bridge transfers, and reward distributions must not be replayed, skipped, mispriced, overpaid, underpaid, or double-claimed.
    * Oracle/rate/provider values, decimals, exchange rates, limits, queues, and external integration balances must not let an attacker extract principal or freeze funds.
    * Only authorized roles may change config, pause, recover assets, set oracles, bridge funds, mint/burn, move delegated assets, or administer vault/pool state.

    Rules:

    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Attacker may be an unprivileged depositor, withdrawer, rsETH holder, wrapper/pool user, reward claimant, bridge user, public function caller, malicious ERC20-style token where accepted, or external contract interacting through supported protocol paths.
    * Do not rely on admin/operator compromise, leaked private keys, malicious maintainer, governance capture, oracle operator compromise, pauser/manager collusion, compromised external protocols, unsupported local configuration, public-mainnet testing, front-running-only attacks, or brute-force DDoS.
    * Exclude dependency-only issues, static-analysis-only findings, gas optimizations, code style, best-practice findings, deployment-only mistakes, and planned designs without code.
    * Exclude test-only code paths, mocks, docs, configs, generated files, local scripts, repo automation, and local tooling.
    * Generate 10 to 20 high-signal questions.
    * At least 70% must be multi-step flow, invariant, authorization, accounting, oracle/rate, share/asset conversion, withdrawal/claim, bridge/wrapper, merkle/replay, or cross-module questions.
    * Every question must be testable by a runnable Foundry PoC, fork-safe test, unit test, fuzz test, invariant test, model test, differential test, or local transaction sequence.
    * Avoid generic checklist questions and repeated root causes; prefer boundary mutations such as stale rates, rounding edges, partial state updates, reentrancy through tokens, duplicate claims, queue desync, failed external calls, paused-state bypass, or cross-chain amount mismatch.
    * Each question must target a plausible issue class for the exact file and scope.

    High-value attack surfaces:

    * Deposit and mint flows: ETH/LST deposits, rsETH minting, pool share issuance, collateral limits, asset support checks, slippage/min amounts, rounding, and token callbacks.
    * Withdrawal and unstaking flows: request accounting, queue state, vault liquidity, claim finalization, unlocked withdrawals, Lido/swETH adapters, and stuck or double-claimable assets.
    * Delegation and vault flows: NodeDelegator asset movement, EigenLayer/Aave/Lido interactions, rewards, fee receiver transfers, recoverability, and role-gated fund movement.
    * Oracle and rate flows: LRTOracle, price feeds, pool collateral oracles, cross-chain rate providers/receivers, stale data, decimals, negative/zero rates, and share/asset conversion.
    * Bridge, wrapper, and pool flows: rsETH/wrsETH/agETH wrapping, bridge messengers, native-chain bridge pools, cross-chain amount accounting, mint/burn authority, and pause gates.
    * Distribution flows: Merkle proof validation, claimed bitmap/index state, KERNEL distributions, unclaimed yield custody, duplicate claims, and gas growth over claim/account lists.

    Impact mapping:

    * Valid impacts: direct theft of user funds, permanent freezing of funds, protocol insolvency, theft/freezing of unclaimed yield, unbounded gas consumption, temporary freezing of funds, failure to deliver promised returns without principal loss, or block stuffing.

    Each question must include:

    1. target function/module;
    2. attacker action;
    3. preconditions;
    4. call sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_module] Can an attacker ACTION under PRECONDITIONS trigger CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: fuzz/state-test PARAMETERS and assert EXPECTED_PROPERTY.",
    ]
    """
    return prompt


def audit_format(question: str) -> str:
    """
    Generate a focused LRT-rsETH exploit-question validation prompt.
    """
    return f"""# QUESTION SCAN PROMPT

## Exploit Question
{question}

## Scope Rules
- Audit only production LRT-rsETH Solidity contracts listed in `scope_files`.
- Do not ask for repo contents or claim files are missing.
- Ignore tests, docs, mocks, generated files, repo automation scripts, configs, build files, IDE files, package metadata, local deployment choices, examples, and local tooling.
- Do not perform public-mainnet testing; prefer local, fork, or private-testnet tests.

## Objective
Decide whether the question leads to a real, reachable LRT-rsETH vulnerability.
The attacker must enter through a supported production path: deposit, mint, burn, withdraw, unstake, claim, wrap, unwrap, pool exchange, bridge/messenger call, merkle distribution, oracle/rate-dependent flow, external token callback, or public contract call.
The impact must match the provided target scope.
Prefer #NoVulnerability unless the path is concrete, locally testable on unmodified code, and proves one of the impacts in `target_scopes`.

## Method
1. Trace the attacker-controlled entrypoint.
2. Map it to exact production contracts/functions.
3. Check relevant guards: role checks, pause gates, asset support, token approvals/callbacks, reentrancy guards, queue state, claim state, amount/fee/decimal accounting, share math, oracle/rate freshness, external integration assumptions, bridge authority, and replay/idempotence protection.
4. Decide whether the questioned invariant can actually break under intended deployment.
5. Prove root cause with file/function/line references.
6. Confirm realistic likelihood and exact scoped impact.
7. Reject if current validation already prevents the exploit.

## Reject Immediately
- Requires admin/operator compromise, leaked private keys, malicious maintainer, governance capture, oracle operator compromise, pauser/manager collusion, external protocol compromise, unsupported local configuration, public-mainnet testing, front-running only, or brute-force DDoS.
- Only affects tests, docs, configs, scripts, mocks, generated code, local tooling, or deployment choices.
- External dependency behavior is the only cause.
- Impact is only ordinary gas optimization, network outage, performance degradation, griefing with no scoped impact, logging/observability, local misconfiguration, harmless rejection, stale read with no fund/security impact, or theoretical risk.
- No concrete scoped impact or no realistic exploit path.

## Allowed Impact Scope
Only these impacts are valid:
- Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield.
- Critical. Permanent freezing of funds.
- Critical. Protocol insolvency.
- High. Theft of unclaimed yield.
- Medium. Unbounded gas consumption.
- Medium. Permanent freezing of unclaimed yield.
- Medium. Temporary freezing of funds.
- Low. Contract fails to deliver promised returns, but doesn't lose value.
- Low. Block stuffing.

## Output
If valid:

### Title
[Clear vulnerability statement] - ([File: file_path])

### Summary
### Finding Description
### Impact Explanation
### Likelihood Explanation
### Recommendation
### Proof of Concept

If invalid, output exactly:
#NoVulnerability found for this question.
"""


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for LRT-rsETH.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Access Rules (Strict)
- Treat production LRT-rsETH Solidity files in the provided scope as accessible context.
- Do not claim missing/inaccessible files.
- Do not ask for repository contents.
- Do not scan tests, docs, build files, IDE files, configs, generated files, resources, package metadata, repo automation scripts, local tooling, or deployment-only choices as audited targets.

## Objective
Use the external report's vulnerability class as a hint to find valid issues based on LRT-rsETH security impact.
Focus on externally reachable issues triggered by an unprivileged depositor, withdrawer, rsETH holder, wrapper/pool user, reward claimant, bridge user, public contract caller, or external contract interacting through supported paths.
Only report an analog if this repository has its own reachable root cause and the impact matches the provided target scope.

## Method
1. Classify vuln type: fund theft, fund freeze, insolvency, role/auth bypass, pause bypass, reentrancy, share/asset mis-accounting, oracle/rate abuse, fee/yield theft, withdrawal queue desync, merkle double claim, bridge/wrapper mint-burn mismatch, unbounded gas, or block stuffing.
2. Map to LRT-rsETH components and exact production files.
3. Prove root cause with exact file/function/module/line references.
4. Confirm concrete scoped impact and realistic likelihood.
5. Explain the attacker-controlled entry path and why this code is a necessary vulnerable step.
6. Reject if the impact does not match the provided target scope.

## Disqualify Immediately
- No reachable attacker-controlled entry path.
- Requires admin/operator compromise, leaked private keys, malicious maintainer, governance capture, oracle operator compromise, pauser/manager collusion, external protocol compromise, unsupported local configuration, public-mainnet testing, front-running only, or brute-force DDoS.
- External dependency behavior is the only cause.
- Test/docs/config/build/generated/local-tooling/deployment-only issue.
- Theoretical-only issue with no protocol impact.
- Impact is only ordinary gas optimization, network outage, performance degradation, griefing without scoped impact, local misconfiguration, observability noise, logging noise, harmless rejection, stale read with no security impact, or non-security correctness.
- Impact or likelihood missing.

## Allowed Impact Scope
Only these impacts are valid:
- Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield.
- Critical. Permanent freezing of funds.
- Critical. Protocol insolvency.
- High. Theft of unclaimed yield.
- Medium. Unbounded gas consumption.
- Medium. Permanent freezing of unclaimed yield.
- Medium. Temporary freezing of funds.
- Low. Contract fails to deliver promised returns, but doesn't lose value.
- Low. Block stuffing.


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
    Generate a strict LRT-rsETH validation prompt for security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md or available program rules for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Reject admin-only, operator-only, trusted-maintainer, leaked-key, best-practice, docs/style, gas-optimization-only, performance-only, griefing-only, front-running-only, static-analysis-only, dependency-only, and purely theoretical issues.
- Reject if the exploit requires unrealistic assumptions, victim mistakes, missing external context, unsupported protocol behavior, governance capture, oracle operator compromise, pauser/manager collusion, external protocol compromise, unsupported local configuration, social engineering, or public-mainnet testing.
- A valid report must be triggerable by an unprivileged external user through deposits, withdrawals, claims, pool/wrapper actions, bridge flows, oracle/rate-dependent public flows, token callbacks, merkle proofs, or other public contract calls.
- The final impact must match one of the `target_scopes`, not just a generic code bug.
- Prefer #NoVulnerability over speculative reports.

## Allowed Impact Scope
Only these impacts are valid:
- Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield.
- Critical. Permanent freezing of funds.
- Critical. Protocol insolvency.
- High. Theft of unclaimed yield.
- Medium. Unbounded gas consumption.
- Medium. Permanent freezing of unclaimed yield.
- Medium. Temporary freezing of funds.
- Low. Contract fails to deliver promised returns, but doesn't lose value.
- Low. Block stuffing.

If the submitted claim does not concretely prove one of the allowed impacts above, it is invalid.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken protocol/security/accounting assumption.
3. Reachable exploit path: preconditions -> attacker action -> trigger -> bad result.
4. Existing checks/guards reviewed and shown insufficient.
5. Concrete impact that exactly matches one allowed LRT-rsETH impact above, with realistic likelihood.
6. Reproducible proof path: Foundry unit/fork/fuzz/invariant test, local transaction sequence, contract call sequence, or justified model/differential test when a fork cannot demonstrate the impact.
7. No obvious rejection reason from SECURITY.md, known audit findings, privileges, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can a normal depositor, withdrawer, rsETH holder, wrapper/pool user, claimant, bridge user, or public caller trigger this?
- Does the code actually behave as claimed?
- Is the impact caused by this repository, not by an external dependency alone?
- Is the fund/yield/freeze/insolvency/gas/block-stuffing impact concrete, not hypothetical?
- Would a responsible-disclosure triager accept the proof?
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
[Concrete allowed LRT-rsETH impact and severity rationale]

## Likelihood Explanation
[Attacker capability, required conditions, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or Foundry fuzz/invariant/fork/model test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt
