import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = "paritytech/polkadot-sdk"
# todo: the name of the repository
REPO_NAME = "polkadot-sdk"

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
    # Core dispatch, validation, and fee accounting
    # =================================================================================
    "substrate/frame/system/src/lib.rs",
    "substrate/frame/system/src/limits.rs",
    "substrate/frame/system/src/extensions/mod.rs",
    "substrate/frame/system/src/extensions/check_nonce.rs",
    "substrate/frame/system/src/extensions/check_weight.rs",
    "substrate/frame/system/src/extensions/check_mortality.rs",
    "substrate/frame/system/src/extensions/authorize_call.rs",
    "substrate/frame/system/src/extensions/weight_reclaim.rs",
    "substrate/frame/transaction-payment/src/lib.rs",
    "substrate/frame/transaction-payment/src/payment.rs",
    "substrate/frame/transaction-payment/src/types.rs",
    "substrate/frame/message-queue/src/lib.rs",
    "substrate/frame/scheduler/src/lib.rs",
    "substrate/frame/scheduler/src/migration.rs",
    "substrate/frame/preimage/src/lib.rs",
    "substrate/frame/preimage/src/migration.rs",
    "substrate/frame/proxy/src/lib.rs",
    "substrate/frame/multisig/src/lib.rs",
    "substrate/frame/multisig/src/migrations.rs",
    "substrate/frame/utility/src/lib.rs",
    "substrate/primitives/runtime/src/lib.rs",
    "substrate/primitives/runtime/src/transaction_validity.rs",
    "substrate/primitives/runtime/src/generic/checked_extrinsic.rs",
    "substrate/primitives/runtime/src/generic/unchecked_extrinsic.rs",
    "substrate/primitives/runtime/src/traits/transaction_extension/mod.rs",
    "substrate/primitives/runtime/src/traits/transaction_extension/dispatch_transaction.rs",
    "substrate/primitives/runtime/src/traits/transaction_extension/as_transaction_extension.rs",
    "substrate/primitives/weights/src/lib.rs",
    "substrate/primitives/weights/src/weight_v2.rs",

    # =================================================================================
    # Assets, staking, and user-funds pallets
    # =================================================================================
    "substrate/frame/balances/src/lib.rs",
    "substrate/frame/balances/src/types.rs",
    "substrate/frame/balances/src/impl_currency.rs",
    "substrate/frame/balances/src/impl_fungible.rs",
    "substrate/frame/balances/src/migration.rs",
    "substrate/frame/assets/src/lib.rs",
    "substrate/frame/assets/src/functions.rs",
    "substrate/frame/assets/src/types.rs",
    "substrate/frame/assets/src/extra_mutator.rs",
    "substrate/frame/assets/src/impl_fungibles.rs",
    "substrate/frame/assets/src/impl_stored_map.rs",
    "substrate/frame/assets/src/migration.rs",
    "substrate/frame/assets-freezer/src/lib.rs",
    "substrate/frame/assets-freezer/src/impls.rs",
    "substrate/frame/asset-conversion/src/lib.rs",
    "substrate/frame/asset-conversion/src/liquidity.rs",
    "substrate/frame/asset-conversion/src/swap.rs",
    "substrate/frame/asset-conversion/src/types.rs",
    "substrate/frame/vesting/src/lib.rs",
    "substrate/frame/vesting/src/vesting_info.rs",
    "substrate/frame/vesting/src/migrations.rs",
    "substrate/frame/staking/src/lib.rs",
    "substrate/frame/staking/src/asset.rs",
    "substrate/frame/staking/src/ledger.rs",
    "substrate/frame/staking/src/slashing.rs",
    "substrate/frame/staking/src/migrations.rs",
    "substrate/frame/staking/src/pallet/mod.rs",
    "substrate/frame/staking/src/pallet/impls.rs",
    "substrate/frame/nfts/src/lib.rs",
    "substrate/frame/nfts/src/common_functions.rs",
    "substrate/frame/nfts/src/impl_nonfungibles.rs",
    "substrate/frame/nfts/src/types.rs",
    "substrate/frame/nfts/src/features/approvals.rs",
    "substrate/frame/nfts/src/features/atomic_swap.rs",
    "substrate/frame/nfts/src/features/attributes.rs",
    "substrate/frame/nfts/src/features/buy_sell.rs",
    "substrate/frame/nfts/src/features/create_delete_collection.rs",
    "substrate/frame/nfts/src/features/create_delete_item.rs",
    "substrate/frame/nfts/src/features/lock.rs",
    "substrate/frame/nfts/src/features/metadata.rs",
    "substrate/frame/nfts/src/features/roles.rs",
    "substrate/frame/nfts/src/features/settings.rs",
    "substrate/frame/nfts/src/features/transfer.rs",
    "substrate/frame/nfts/src/migration.rs",
    "substrate/frame/nft-fractionalization/src/lib.rs",
    "substrate/frame/nft-fractionalization/src/types.rs",
    "substrate/frame/treasury/src/lib.rs",
    "substrate/frame/treasury/src/migration.rs",

    # =================================================================================
    # Contracts and execution environments
    # =================================================================================
    "substrate/frame/contracts/src/lib.rs",
    "substrate/frame/contracts/src/address.rs",
    "substrate/frame/contracts/src/chain_extension.rs",
    "substrate/frame/contracts/src/exec.rs",
    "substrate/frame/contracts/src/gas.rs",
    "substrate/frame/contracts/src/primitives.rs",
    "substrate/frame/contracts/src/schedule.rs",
    "substrate/frame/contracts/src/storage.rs",
    "substrate/frame/contracts/src/transient_storage.rs",
    "substrate/frame/contracts/src/migration.rs",
    "substrate/frame/contracts/src/storage/meter.rs",
    "substrate/frame/contracts/src/wasm/mod.rs",
    "substrate/frame/contracts/src/wasm/prepare.rs",
    "substrate/frame/contracts/src/wasm/runtime.rs",
    "substrate/frame/revive/src/lib.rs",
    "substrate/frame/revive/src/address.rs",
    "substrate/frame/revive/src/access_list.rs",
    "substrate/frame/revive/src/call_builder.rs",
    "substrate/frame/revive/src/deposit_payment.rs",
    "substrate/frame/revive/src/evm.rs",
    "substrate/frame/revive/src/exec.rs",
    "substrate/frame/revive/src/impl_fungibles.rs",
    "substrate/frame/revive/src/limits.rs",
    "substrate/frame/revive/src/precompiles.rs",
    "substrate/frame/revive/src/primitives.rs",
    "substrate/frame/revive/src/storage.rs",
    "substrate/frame/revive/src/transient_storage.rs",
    "substrate/frame/revive/src/metering/mod.rs",
    "substrate/frame/revive/src/metering/gas.rs",
    "substrate/frame/revive/src/metering/weight.rs",
    "substrate/frame/revive/src/metering/storage.rs",
    "substrate/frame/revive/src/metering/math.rs",
    "substrate/frame/revive/src/evm/call.rs",
    "substrate/frame/revive/src/evm/fees.rs",
    "substrate/frame/revive/src/evm/runtime.rs",
    "substrate/frame/revive/src/evm/tx_extension.rs",
    "substrate/frame/revive/src/evm/transfer_with_dust.rs",
    "substrate/frame/revive/src/vm/mod.rs",
    "substrate/frame/revive/src/vm/pvm.rs",
    "substrate/frame/revive/src/vm/evm.rs",
    "substrate/frame/revive/src/vm/runtime_costs.rs",
    "substrate/frame/revive/src/vm/evm/interpreter.rs",
    "substrate/frame/revive/src/vm/evm/memory.rs",
    "substrate/frame/revive/src/vm/evm/stack.rs",
    "substrate/frame/revive/src/vm/evm/ext_bytecode.rs",
    "substrate/frame/revive/src/vm/evm/util.rs",
    "substrate/frame/revive/src/vm/evm/instructions/mod.rs",
    "substrate/frame/revive/src/vm/evm/instructions/arithmetic.rs",
    "substrate/frame/revive/src/vm/evm/instructions/bitwise.rs",
    "substrate/frame/revive/src/vm/evm/instructions/block_info.rs",
    "substrate/frame/revive/src/vm/evm/instructions/control.rs",
    "substrate/frame/revive/src/vm/evm/instructions/contract.rs",
    "substrate/frame/revive/src/vm/evm/instructions/contract/call_helpers.rs",
    "substrate/frame/revive/src/vm/evm/instructions/host.rs",
    "substrate/frame/revive/src/vm/evm/instructions/memory.rs",
    "substrate/frame/revive/src/vm/evm/instructions/stack.rs",
    "substrate/frame/revive/src/vm/evm/instructions/system.rs",
    "substrate/frame/revive/src/vm/evm/instructions/tx_info.rs",
    "substrate/frame/revive/src/vm/evm/instructions/utility.rs",

    # =================================================================================
    # XCM and cross-chain execution libraries
    # =================================================================================
    "polkadot/xcm/pallet-xcm/src/lib.rs",
    "polkadot/xcm/pallet-xcm/src/errors.rs",
    "polkadot/xcm/pallet-xcm/src/migration.rs",
    "polkadot/xcm/pallet-xcm/src/transfer_assets_validation.rs",
    "polkadot/xcm/pallet-xcm/src/xcm_helpers.rs",
    "polkadot/xcm/xcm-builder/src/lib.rs",
    "polkadot/xcm/xcm-builder/src/asset_conversion.rs",
    "polkadot/xcm/xcm-builder/src/barriers.rs",
    "polkadot/xcm/xcm-builder/src/controller.rs",
    "polkadot/xcm/xcm-builder/src/fee_handling.rs",
    "polkadot/xcm/xcm-builder/src/filter_asset_location.rs",
    "polkadot/xcm/xcm-builder/src/forwarder.rs",
    "polkadot/xcm/xcm-builder/src/fungible_adapter.rs",
    "polkadot/xcm/xcm-builder/src/fungibles_adapter.rs",
    "polkadot/xcm/xcm-builder/src/location_conversion.rs",
    "polkadot/xcm/xcm-builder/src/matcher.rs",
    "polkadot/xcm/xcm-builder/src/matches_location.rs",
    "polkadot/xcm/xcm-builder/src/matches_token.rs",
    "polkadot/xcm/xcm-builder/src/nonfungible_adapter.rs",
    "polkadot/xcm/xcm-builder/src/nonfungibles_adapter.rs",
    "polkadot/xcm/xcm-builder/src/origin_aliases.rs",
    "polkadot/xcm/xcm-builder/src/origin_conversion.rs",
    "polkadot/xcm/xcm-builder/src/pay.rs",
    "polkadot/xcm/xcm-builder/src/process_xcm_message.rs",
    "polkadot/xcm/xcm-builder/src/routing.rs",
    "polkadot/xcm/xcm-builder/src/transactional.rs",
    "polkadot/xcm/xcm-builder/src/transfer.rs",
    "polkadot/xcm/xcm-builder/src/universal_exports.rs",
    "polkadot/xcm/xcm-builder/src/asset_exchange/mod.rs",
    "polkadot/xcm/xcm-builder/src/asset_exchange/single_asset_adapter/adapter.rs",
    "polkadot/xcm/xcm-executor/src/lib.rs",
    "polkadot/xcm/xcm-executor/src/assets.rs",
    "polkadot/xcm/xcm-executor/src/config.rs",
    "polkadot/xcm/xcm-executor/src/traits/mod.rs",
    "polkadot/xcm/xcm-executor/src/traits/asset_exchange.rs",
    "polkadot/xcm/xcm-executor/src/traits/asset_lock.rs",
    "polkadot/xcm/xcm-executor/src/traits/asset_transfer.rs",
    "polkadot/xcm/xcm-executor/src/traits/conversion.rs",
    "polkadot/xcm/xcm-executor/src/traits/drop_assets.rs",
    "polkadot/xcm/xcm-executor/src/traits/event_emitter.rs",
    "polkadot/xcm/xcm-executor/src/traits/export.rs",
    "polkadot/xcm/xcm-executor/src/traits/fee_manager.rs",
    "polkadot/xcm/xcm-executor/src/traits/hrmp.rs",
    "polkadot/xcm/xcm-executor/src/traits/on_response.rs",
    "polkadot/xcm/xcm-executor/src/traits/process_transaction.rs",
    "polkadot/xcm/xcm-executor/src/traits/record_xcm.rs",
    "polkadot/xcm/xcm-executor/src/traits/should_execute.rs",
    "polkadot/xcm/xcm-executor/src/traits/token_matching.rs",
    "polkadot/xcm/xcm-executor/src/traits/transact_asset.rs",
    "polkadot/xcm/xcm-executor/src/traits/weight.rs",
    "polkadot/xcm/src/lib.rs",
    "polkadot/xcm/src/double_encoded.rs",
    "polkadot/xcm/src/v5/mod.rs",
    "polkadot/xcm/src/v5/asset.rs",
    "polkadot/xcm/src/v5/junction.rs",
    "polkadot/xcm/src/v5/junctions.rs",
    "polkadot/xcm/src/v5/location.rs",
    "polkadot/xcm/src/v5/traits.rs",
    "polkadot/xcm/src/v4/mod.rs",
    "polkadot/xcm/src/v4/asset.rs",
    "polkadot/xcm/src/v4/junction.rs",
    "polkadot/xcm/src/v4/junctions.rs",
    "polkadot/xcm/src/v4/location.rs",
    "polkadot/xcm/src/v4/traits.rs",
    "polkadot/xcm/src/v3/mod.rs",
    "polkadot/xcm/src/v3/junction.rs",
    "polkadot/xcm/src/v3/junctions.rs",
    "polkadot/xcm/src/v3/multiasset.rs",
    "polkadot/xcm/src/v3/multilocation.rs",
    "polkadot/xcm/src/v3/traits.rs",

    # =================================================================================
    # Cumulus and relay-chain parachain logic
    # =================================================================================
    "cumulus/pallets/xcm/src/lib.rs",
    "cumulus/pallets/dmp-queue/src/lib.rs",
    "cumulus/pallets/dmp-queue/src/migration.rs",
    "cumulus/pallets/xcmp-queue/src/lib.rs",
    "cumulus/pallets/xcmp-queue/src/migration/mod.rs",
    "cumulus/pallets/xcmp-queue/src/migration/v5.rs",
    "cumulus/pallets/xcmp-queue/src/migration/v6.rs",
    "cumulus/pallets/xcmp-queue/src/migration/v7.rs",
    "cumulus/pallets/parachain-system/src/lib.rs",
    "cumulus/pallets/parachain-system/src/block_weight/mod.rs",
    "cumulus/pallets/parachain-system/src/block_weight/pre_inherents_hook.rs",
    "cumulus/pallets/parachain-system/src/block_weight/transaction_extension.rs",
    "cumulus/pallets/parachain-system/src/consensus_hook.rs",
    "cumulus/pallets/parachain-system/src/descendant_validation.rs",
    "cumulus/pallets/parachain-system/src/migration.rs",
    "cumulus/pallets/parachain-system/src/parachain_inherent.rs",
    "cumulus/pallets/parachain-system/src/relay_state_snapshot.rs",
    "cumulus/pallets/parachain-system/src/unincluded_segment.rs",
    "cumulus/pallets/parachain-system/src/validate_block/mod.rs",
    "cumulus/pallets/parachain-system/src/validate_block/implementation.rs",
    "cumulus/pallets/parachain-system/src/validate_block/scheduling.rs",
    "cumulus/pallets/parachain-system/src/validate_block/trie_cache.rs",
    "cumulus/pallets/parachain-system/src/validate_block/trie_recorder.rs",
    "cumulus/pallets/weight-reclaim/src/lib.rs",
    "cumulus/primitives/core/src/lib.rs",
    "cumulus/primitives/core/src/parachain_block_data.rs",
    "cumulus/primitives/core/src/scheduling.rs",
    "cumulus/primitives/parachain-inherent/src/lib.rs",
    "cumulus/primitives/storage-weight-reclaim/src/lib.rs",
    "cumulus/primitives/utility/src/lib.rs",
    "polkadot/runtime/common/src/lib.rs",
    "polkadot/runtime/common/src/impls.rs",
    "polkadot/runtime/common/src/slot_range.rs",
    "polkadot/runtime/common/src/xcm_sender.rs",
    "polkadot/runtime/common/src/assigned_slots/mod.rs",
    "polkadot/runtime/common/src/assigned_slots/migration.rs",
    "polkadot/runtime/common/src/auctions/mod.rs",
    "polkadot/runtime/common/src/claims/mod.rs",
    "polkadot/runtime/common/src/crowdloan/mod.rs",
    "polkadot/runtime/common/src/crowdloan/migration.rs",
    "polkadot/runtime/common/src/paras_registrar/mod.rs",
    "polkadot/runtime/common/src/paras_registrar/migration.rs",
    "polkadot/runtime/common/src/purchase/mod.rs",
    "polkadot/runtime/common/src/slots/mod.rs",
    "polkadot/runtime/common/src/slots/migration.rs",
    "polkadot/runtime/parachains/src/lib.rs",
    "polkadot/runtime/parachains/src/configuration.rs",
    "polkadot/runtime/parachains/src/configuration/migration.rs",
    "polkadot/runtime/parachains/src/coretime/mod.rs",
    "polkadot/runtime/parachains/src/dmp.rs",
    "polkadot/runtime/parachains/src/dmp/inbound_downward_queue.rs",
    "polkadot/runtime/parachains/src/dmp/migration.rs",
    "polkadot/runtime/parachains/src/hrmp.rs",
    "polkadot/runtime/parachains/src/inclusion/mod.rs",
    "polkadot/runtime/parachains/src/inclusion/migration.rs",
    "polkadot/runtime/parachains/src/initializer.rs",
    "polkadot/runtime/parachains/src/on_demand/mod.rs",
    "polkadot/runtime/parachains/src/on_demand/migration.rs",
    "polkadot/runtime/parachains/src/origin.rs",
    "polkadot/runtime/parachains/src/paras/mod.rs",
    "polkadot/runtime/parachains/src/paras_inherent/mod.rs",
    "polkadot/runtime/parachains/src/paras_inherent/misc.rs",
    "polkadot/runtime/parachains/src/reward_points.rs",
    "polkadot/runtime/parachains/src/scheduler.rs",
    "polkadot/runtime/parachains/src/scheduler/assigner_coretime/mod.rs",
    "polkadot/runtime/parachains/src/scheduler/migration.rs",
    "polkadot/runtime/parachains/src/shared.rs",
    "polkadot/runtime/parachains/src/shared/migration.rs",
    "polkadot/runtime/parachains/src/util.rs",
]


target_scopes = [
    "Critical. Unauthorized mint, burn, withdraw, pool drain, double-claim, lease seizure, or accounting mismatch reachable by a normal user in `substrate/frame/{balances,assets,assets-freezer,asset-conversion,vesting,staking,nfts,nft-fractionalization,treasury}/src/*` or `polkadot/runtime/common/src/{claims,crowdloan,assigned_slots,purchase,paras_registrar,auctions,slots}/*`, causing direct theft, unbacked value, or permanent asset loss/freeze",
    "Critical. Signature, nonce, origin, proxy, multisig, preimage, scheduler, or dispatch-validation bypass in `substrate/frame/{system,proxy,multisig,utility,preimage,scheduler,transaction-payment}/src/*` or `substrate/primitives/runtime/src/{generic/*,traits/transaction_extension/*,transaction_validity.rs}` allowing an unprivileged user to replay effects, act as another account, skip required checks, or reach privileged behavior",
    "Critical. Contract, precompile, VM, or metering flaw in `substrate/frame/{contracts,revive}/src/**/*` that lets a normal user or contract caller steal funds, corrupt storage, escape intended call context, bypass gas/weight/storage limits, or obtain unauthorized execution",
    "Critical. XCM barrier, origin-conversion, asset-transactor, router, fee, or filter bypass in `polkadot/xcm/{pallet-xcm,xcm-builder,xcm-executor,src}/**/*` or `cumulus/pallets/{xcm,xcmp-queue,dmp-queue,parachain-system,weight-reclaim}/src/**/*` allowing a supported user or XCM path to move assets or execute calls it should not reach",
    "Critical. Parachain lifecycle, registrar, crowdloan, claim, queue, or state-transition flaw in `polkadot/runtime/common/src/{lib.rs,impls.rs,xcm_sender.rs,claims/*,crowdloan/*,assigned_slots/*,purchase/*,paras_registrar/*,auctions/*,slots/*}` or `polkadot/runtime/parachains/src/{lib.rs,configuration.rs,shared.rs,origin.rs,dmp.rs,hrmp.rs,inclusion/*,scheduler.rs,coretime/mod.rs,on_demand/mod.rs,initializer.rs,paras/mod.rs}` that lets an unprivileged user seize resources, create unauthorized state changes, or permanently trap funds/messages",
    "Critical. Validation or block-weight bug in `cumulus/pallets/parachain-system/src/{lib.rs,descendant_validation.rs,parachain_inherent.rs,relay_state_snapshot.rs,validate_block/*,block_weight/*}` or `cumulus/primitives/{core,parachain-inherent,utility,storage-weight-reclaim}/src/*` enabling user-controlled data to be accepted, replayed, or mis-accounted beyond intended bounds",
    "High. Crafted but valid user input causes a chain-wide or long-lived halt, stuck queue, or unrecoverable service degradation in `substrate/frame/{system,message-queue,contracts,revive}/src/*`, `polkadot/xcm/**/*`, `cumulus/pallets/**/*`, or `polkadot/runtime/parachains/src/**/*` without requiring control of a node, peer, validator, collator, or relayer",
    "High. Reachable fee, weight, refund, storage-metering, or queue-accounting asymmetry in `substrate/frame/{system,transaction-payment,contracts,revive}/src/*`, `substrate/primitives/weights/src/*`, `polkadot/xcm/**/*`, or `cumulus/pallets/{xcmp-queue,dmp-queue,parachain-system,weight-reclaim}/src/*` lets a normal user obtain underpriced execution, grief critical paths at low cost, or force persistent accounting inconsistency",
]


scope_scan = [
]
def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit + fuzzing questions for one Polkadot SDK target.

    ```
    target_file format:
    "'File Name: substrate/frame/assets/src/lib.rs -> Scope: Critical. Unauthorized asset accounting break'"
    """

    prompt = f"""
    ```
    
    Generate exploit-focused security audit and fuzzing questions for this exact Polkadot SDK target:
    
    {target_file}
    
    Project focus:
    This repo covers Substrate FRAME pallets, runtime primitives, contracts/revive execution, XCM libraries, Cumulus parachain support, and relay-chain parachain logic. Focus on implementation bugs reachable without privileged access, especially asset/accounting breaks, origin/dispatch bypasses, contract or precompile flaws, XCM/message-routing failures, and user-triggered halts.

    Rules:
    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Rust symbols when possible.
    * Attacker is unprivileged only: a normal signed user, proxy or multisig participant, contract caller, or attacker-controlled account using supported extrinsic/XCM paths.
    * Never assume admin, governance, sudo, validator, collator, relayer, operator, node, peer, or leaked keys.
    * Do not rely on mocked origins, handcrafted internal helpers, direct storage writes, impossible external-chain assumptions, or bridge-only trust assumptions.
    * Generate 10 to 18 high-signal questions.
    * At least 70% must be multi-step flow, invariant, accounting, origin, replay, XCM, contract-execution, queue, or cross-module questions.
    * Every question must be testable by unit test, integration test, xcm-simulator/xcm-emulator test, fuzz test, invariant test, or differential test.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * No unprivileged user can mint, unlock, move, or burn assets they do not control.
    * Signatures, nonces, origins, proxy approvals, multisig approvals, and XCM origins must not be forgeable, stale-reusable, or replayable.
    * Contract/precompile execution must not escape intended caller, asset, or storage boundaries.
    * XCM, fee, weight, gas, storage, and queue accounting must stay consistent and not be bypassed.
    * Runtime behaviour must stay deterministic and must not admit unauthorized privileged calls.
    * Crafted but valid user input must not permanently halt critical queues, validation paths, or freeze user funds.

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
    "[File: {target_file}] [Function: symbol_or_module] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: test/fuzz PARAMETERS and assert EXPECTED_PROPERTY.",
    ]
    """
    return prompt

def audit_format(security_question: str) -> str:
    """
    Generate a focused Polkadot SDK exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- The referenced file/path exists. Do not say files are missing.
- Do not ask for code. Use available repository context.
- Analyze only this question and only the scoped impact.
- Attacker is unprivileged only: a signed user, proxy or multisig participant, contract caller, or attacker-controlled account using real extrinsic/XCM paths.
- Ignore admin-only, governance-only, node-only, relayer-only, leaked-key, docs, style, gas-only, and best-practice issues.
- Privileged functions matter only if they create a later user-triggered exploit path.
- Do not rely on mocked origins, direct helper calls, direct storage mutation, malicious peers/nodes, or impossible external-chain assumptions.

## Mission
Prove or disprove this as a real Polkadot SDK bug.

Check:
- exact reachable Rust path;
- attacker-controlled entry path from extrinsic, proxy, multisig, contract/precompile, XCM, or runtime-dispatch flow;
- state changes before/after asset, accounting, queue, contract, or parachain transitions;
- whether signature, nonce, origin, filter, barrier, proxy, fee, weight, gas, storage, or queue checks stop it;
- whether the scoped impact is concrete;
- whether a Rust unit/integration test, xcm-simulator/xcm-emulator test, or fuzz/invariant test can reproduce it.

## Core Invariants
- User-controlled assets must remain fully backed and cannot be stolen, duplicated, or permanently frozen.
- Signatures, nonces, origins, proxy approvals, multisig approvals, contract call context, and XCM origins must not be forgeable or replayable.
- Contracts, precompiles, and XCM messages must only execute through intended routes with correct accounting.
- Fee, weight, gas, storage, and queue logic must not be bypassable by normal users.
- The runtime must not accept unauthorized privileged state transitions.
- Critical queues and validation paths must not be permanently halted by valid user input.

## Valid Only If
1. Exact file/function/line range exists.
2. Root cause is a real missing check, bad accounting, replay, origin confusion, unsafe parsing, or logic error.
3. Exploit path is: preconditions -> attacker action/data -> trigger -> bad state/result.
4. Existing protections are reviewed and insufficient.
5. Impact matches the scoped impact.
6. PoC/test idea has clear assertions.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker inputs, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact]

### Likelihood Explanation
[Preconditions, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Rust integration test, xcm-simulator/xcm-emulator test, or fuzz/invariant test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for Polkadot SDK security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Reject admin-only, governance-only, node-only, relayer-only, leaked-key, best-practice, docs/style, gas-only, mocked-path, and purely theoretical issues.
- Reject if the exploit requires unrealistic assumptions, victim mistakes, direct storage mutation, mocked XCM/origins, or unsupported protocol behavior.
- A valid report must be triggerable by an unprivileged user, unless the claim proves privilege escalation from a user path.
- The final impact must match an in-scope Polkadot SDK implementation impact, not a separate bridge-only program or a generic code bug.
- Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken security/accounting assumption.
3. Reachable exploit path: preconditions -> attacker action -> trigger -> bad result.
4. Existing checks/guards reviewed and shown insufficient.
5. Concrete in-scope impact with realistic likelihood.
6. Reproducible proof path: unit PoC, fork test, invariant/fuzz test, or exact manual steps.
7. No obvious rejection reason from SECURITY.md, known issues, privileges, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can a normal external user trigger this through a real extrinsic, contract, parachain, or XCM path?
- Does the code actually behave as claimed?
- Is the impact caused by the SDK code, not by a malicious node, peer, or external dependency alone?
- Is the loss/freeze/insolvency concrete, not hypothetical?
- Would a bounty triager accept the proof?
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
[Concrete in-scope impact and severity rationale]

## Likelihood Explanation
[Attacker capability, required conditions, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or fuzz/invariant/fork test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for Polkadot SDK.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Access Rules (Strict)
- Treat in-scope SDK files as accessible context.
- Do not claim missing/inaccessible files.
- Do not ask for repository contents.

## Objective
Find whether the same vulnerability class can occur in this repo's in-scope Polkadot SDK code.
Use the external report as a hint, not as proof.

Note: Check SECURITY.md / Researcher.Md and think in this actual way.
Note: Never generate a report that would result in an out-of-scope and rejected vulnerability.

## Method
1. Classify vuln type (auth, accounting, state transition, parsing/deserialization, crypto, replay, reentrancy, DoS).
2. Map the vulnerability pattern to FRAME pallets, runtime primitives, contracts/revive, XCM, Cumulus, or relay-chain parachain logic to find a valid analog.
3. Prove root cause with exact file/function/line references in the codebase.
4. Confirm concrete impact + realistic likelihood for an unprivileged user.

## Disqualify Immediately
- No reachable attacker-controlled entry path.
- Trusted-role compromise required.
- Only mocked XCM/origin/helper paths are shown.
- The path is bridge-only, node-only, peer-only, or otherwise outside the active program focus.
- Theoretical-only issue with no protocol impact.
- Impact or likelihood missing.

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
