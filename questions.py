import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 25
# todo: the path from https://github.com/Chia-Network/chia-blockchain
SOURCE_REPO = "Chia-Network/chia-blockchain"
# todo: the name of the repository
REPO_NAME = "chia-blockchain"
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
    "chia/consensus/augmented_chain.py",
    "chia/consensus/block_body_validation.py",
    "chia/consensus/block_creation.py",
    "chia/consensus/block_header_validation.py",
    "chia/consensus/block_height_map.py",
    "chia/consensus/block_height_map_protocol.py",
    "chia/consensus/block_record.py",
    "chia/consensus/block_rewards.py",
    "chia/consensus/blockchain.py",
    "chia/consensus/blockchain_interface.py",
    "chia/consensus/blockchain_mmr.py",
    "chia/consensus/challenge_tree.py",
    "chia/consensus/coin_store_protocol.py",
    "chia/consensus/coinbase.py",
    "chia/consensus/condition_costs.py",
    "chia/consensus/condition_tools.py",
    "chia/consensus/constants.py",
    "chia/consensus/default_constants.py",
    "chia/consensus/deficit.py",
    "chia/consensus/difficulty_adjustment.py",
    "chia/consensus/find_fork_point.py",
    "chia/consensus/full_block_to_block_record.py",
    "chia/consensus/generator_tools.py",
    "chia/consensus/get_block_challenge.py",
    "chia/consensus/get_block_generator.py",
    "chia/consensus/make_sub_epoch_summary.py",
    "chia/consensus/mmr.py",
    "chia/consensus/multiprocess_validation.py",
    "chia/consensus/pos_quality.py",
    "chia/consensus/pot_iterations.py",
    "chia/consensus/prev_transaction_block.py",
    "chia/consensus/signage_point.py",
    "chia/consensus/stub_mmr_manager.py",
    "chia/consensus/vdf_info_computation.py",
    "chia/daemon/client.py",
    "chia/daemon/keychain_proxy.py",
    "chia/daemon/keychain_server.py",
    "chia/daemon/server.py",
    "chia/daemon/windows_signal.py",
    "chia/data_layer/data_layer.py",
    "chia/data_layer/data_layer_api.py",
    "chia/data_layer/data_layer_errors.py",
    "chia/data_layer/data_layer_rpc_api.py",
    "chia/data_layer/data_layer_rpc_util.py",
    "chia/data_layer/data_layer_server.py",
    "chia/data_layer/data_layer_service.py",
    "chia/data_layer/data_layer_util.py",
    "chia/data_layer/data_layer_wallet.py",
    "chia/data_layer/data_store.py",
    "chia/data_layer/dl_wallet_store.py",
    "chia/data_layer/download_data.py",
    "chia/data_layer/s3_plugin_service.py",
    "chia/data_layer/singleton_record.py",
    "chia/data_layer/util/plugin.py",
    "chia/farmer/farmer.py",
    "chia/farmer/farmer_api.py",
    "chia/farmer/farmer_rpc_api.py",
    "chia/farmer/farmer_service.py",
    "chia/full_node/bitcoin_fee_estimator.py",
    "chia/full_node/block_store.py",
    "chia/full_node/bundle_tools.py",
    "chia/full_node/check_fork_next_block.py",
    "chia/full_node/coin_store.py",
    "chia/full_node/eligible_coin_spends.py",
    "chia/full_node/fee_estimate_store.py",
    "chia/full_node/fee_estimation.py",
    "chia/full_node/fee_estimator.py",
    "chia/full_node/fee_estimator_constants.py",
    "chia/full_node/fee_estimator_interface.py",
    "chia/full_node/fee_history.py",
    "chia/full_node/fee_tracker.py",
    "chia/full_node/full_block_utils.py",
    "chia/full_node/full_node.py",
    "chia/full_node/full_node_api.py",
    "chia/full_node/full_node_rpc_api.py",
    "chia/full_node/full_node_service.py",
    "chia/full_node/full_node_store.py",
    "chia/full_node/hard_fork_utils.py",
    "chia/full_node/hint_management.py",
    "chia/full_node/hint_store.py",
    "chia/full_node/mempool.py",
    "chia/full_node/mempool_manager.py",
    "chia/full_node/pending_tx_cache.py",
    "chia/full_node/subscriptions.py",
    "chia/full_node/sync_store.py",
    "chia/full_node/tx_processing_queue.py",
    "chia/full_node/weight_proof.py",
    "chia/harvester/harvester.py",
    "chia/harvester/harvester_api.py",
    "chia/harvester/harvester_rpc_api.py",
    "chia/harvester/harvester_service.py",
    "chia/plot_sync/delta.py",
    "chia/plot_sync/exceptions.py",
    "chia/plot_sync/receiver.py",
    "chia/plot_sync/sender.py",
    "chia/plot_sync/util.py",
    "chia/pools/claim_pool_rewards_dpuz.clsp",
    "chia/pools/forward_to_pool_puzzle_hash_dpuz.clsp",
    "chia/pools/plotnft_drivers.py",
    "chia/pools/pool_config.py",
    "chia/pools/pool_puzzles.py",
    "chia/pools/pool_wallet.py",
    "chia/pools/pool_wallet_info.py",
    "chia/protocols/farmer_protocol.py",
    "chia/protocols/fee_estimate.py",
    "chia/protocols/full_node_protocol.py",
    "chia/protocols/harvester_protocol.py",
    "chia/protocols/introducer_protocol.py",
    "chia/protocols/outbound_message.py",
    "chia/protocols/pool_protocol.py",
    "chia/protocols/protocol_message_type_to_node_type.py",
    "chia/protocols/protocol_message_types.py",
    "chia/protocols/protocol_state_machine.py",
    "chia/protocols/protocol_timing.py",
    "chia/protocols/shared_protocol.py",
    "chia/protocols/solver_protocol.py",
    "chia/protocols/timelord_protocol.py",
    "chia/protocols/wallet_protocol.py",
    "chia/rpc/rpc_client.py",
    "chia/rpc/rpc_errors.py",
    "chia/rpc/rpc_server.py",
    "chia/rpc/util.py",
    "chia/seeder/crawl_store.py",
    "chia/seeder/crawler.py",
    "chia/seeder/crawler_api.py",
    "chia/seeder/crawler_rpc_api.py",
    "chia/seeder/crawler_service.py",
    "chia/seeder/dns_server.py",
    "chia/seeder/peer_record.py",
    "chia/server/address_manager.py",
    "chia/server/address_manager_store.py",
    "chia/server/api_protocol.py",
    "chia/server/capabilities.py",
    "chia/server/chia_policy.py",
    "chia/server/introducer_peers.py",
    "chia/server/node_discovery.py",
    "chia/server/rate_limit_numbers.py",
    "chia/server/rate_limits.py",
    "chia/server/rate_limits_v3.py",
    "chia/server/resolve_peer_info.py",
    "chia/server/server.py",
    "chia/server/signal_handlers.py",
    "chia/server/ssl_context.py",
    "chia/server/upnp.py",
    "chia/server/ws_connection.py",
    "chia/timelord/iters_from_block.py",
    "chia/timelord/timelord.py",
    "chia/timelord/timelord_api.py",
    "chia/timelord/timelord_launcher.py",
    "chia/timelord/timelord_rpc_api.py",
    "chia/timelord/timelord_service.py",
    "chia/timelord/timelord_state.py",
    "chia/timelord/types.py",
    "chia/types/block_protocol.py",
    "chia/types/blockchain_format/classgroup.py",
    "chia/types/blockchain_format/coin.py",
    "chia/types/blockchain_format/program.py",
    "chia/types/blockchain_format/proof_of_space.py",
    "chia/types/blockchain_format/serialized_program.py",
    "chia/types/blockchain_format/tree_hash.py",
    "chia/types/blockchain_format/vdf.py",
    "chia/types/clvm_cost.py",
    "chia/types/coin_spend.py",
    "chia/types/condition_opcodes.py",
    "chia/types/condition_with_args.py",
    "chia/types/fee_rate.py",
    "chia/types/generator_types.py",
    "chia/types/internal_mempool_item.py",
    "chia/types/mempool_inclusion_status.py",
    "chia/types/mempool_item.py",
    "chia/types/mempool_submission_status.py",
    "chia/types/mojos.py",
    "chia/types/peer_info.py",
    "chia/types/signing_mode.py",
    "chia/types/unfinished_header_block.py",
    "chia/types/validation_state.py",
    "chia/types/weight_proof.py",
    "chia/util/action_scope.py",
    "chia/util/async_pool.py",
    "chia/util/batches.py",
    "chia/util/bech32m.py",
    "chia/util/beta_metrics.py",
    "chia/util/block_cache.py",
    "chia/util/byte_types.py",
    "chia/util/casts.py",
    "chia/util/chia_logging.py",
    "chia/util/chia_version.py",
    "chia/util/collection.py",
    "chia/util/config.py",
    "chia/util/cpu.py",
    "chia/util/db_synchronous.py",
    "chia/util/db_version.py",
    "chia/util/db_wrapper.py",
    "chia/util/default_root.py",
    "chia/util/errors.py",
    "chia/util/file_keyring.py",
    "chia/util/files.py",
    "chia/util/harvester_config.py",
    "chia/util/hash.py",
    "chia/util/inline_executor.py",
    "chia/util/ip_address.py",
    "chia/util/json_util.py",
    "chia/util/keychain.py",
    "chia/util/keyring_wrapper.py",
    "chia/util/limited_semaphore.py",
    "chia/util/lock.py",
    "chia/util/log_exceptions.py",
    "chia/util/logging.py",
    "chia/util/lru_cache.py",
    "chia/util/math.py",
    "chia/util/network.py",
    "chia/util/paginator.py",
    "chia/util/path.py",
    "chia/util/permissions.py",
    "chia/util/priority_mutex.py",
    "chia/util/priority_thread_pool_executor.py",
    "chia/util/profiler.py",
    "chia/util/recursive_replace.py",
    "chia/util/safe_cancel_task.py",
    "chia/util/service_groups.py",
    "chia/util/setproctitle.py",
    "chia/util/significant_bits.py",
    "chia/util/streamable.py",
    "chia/util/task_pipeline.py",
    "chia/util/task_referencer.py",
    "chia/util/task_timing.py",
    "chia/util/timing.py",
    "chia/util/virtual_project_analysis.py",
    "chia/util/ws_message.py",
    "chia/wallet/cat_wallet/cat_constants.py",
    "chia/wallet/cat_wallet/cat_info.py",
    "chia/wallet/cat_wallet/cat_outer_puzzle.py",
    "chia/wallet/cat_wallet/cat_utils.py",
    "chia/wallet/cat_wallet/cat_wallet.py",
    "chia/wallet/cat_wallet/lineage_store.py",
    "chia/wallet/cat_wallet/r_cat_wallet.py",
    "chia/wallet/coin_selection.py",
    "chia/wallet/conditions.py",
    "chia/wallet/db_wallet/db_wallet_puzzles.py",
    "chia/wallet/derivation_record.py",
    "chia/wallet/derive_keys.py",
    "chia/wallet/did_wallet/did_info.py",
    "chia/wallet/did_wallet/did_wallet.py",
    "chia/wallet/did_wallet/did_wallet_puzzles.py",
    "chia/wallet/driver_protocol.py",
    "chia/wallet/estimate_fees.py",
    "chia/wallet/key_val_store.py",
    "chia/wallet/lineage_proof.py",
    "chia/wallet/nft_wallet/metadata_outer_puzzle.py",
    "chia/wallet/nft_wallet/nft_info.py",
    "chia/wallet/nft_wallet/nft_puzzle_utils.py",
    "chia/wallet/nft_wallet/nft_puzzles.py",
    "chia/wallet/nft_wallet/nft_wallet.py",
    "chia/wallet/nft_wallet/ownership_outer_puzzle.py",
    "chia/wallet/nft_wallet/singleton_outer_puzzle.py",
    "chia/wallet/nft_wallet/transfer_program_puzzle.py",
    "chia/wallet/nft_wallet/uncurry_nft.py",
    "chia/wallet/notification_manager.py",
    "chia/wallet/notification_store.py",
    "chia/wallet/outer_puzzles.py",
    "chia/wallet/plotnft_wallet/plotnft_store.py",
    "chia/wallet/plotnft_wallet/plotnft_wallet.py",
    "chia/wallet/puzzle_drivers.py",
    "chia/wallet/puzzles/clawback/drivers.py",
    "chia/wallet/puzzles/clawback/metadata.py",
    "chia/wallet/puzzles/clawback/puzzle_decorator.py",
    "chia/wallet/puzzles/condition_codes.clib",
    "chia/wallet/puzzles/curry.clib",
    "chia/wallet/puzzles/custody/custody_architecture.py",
    "chia/wallet/puzzles/custody/fixed_create_coin_destinations.clsp",
    "chia/wallet/puzzles/custody/heightlock.clsp",
    "chia/wallet/puzzles/custody/member_puzzles.py",
    "chia/wallet/puzzles/custody/restriction_utilities.py",
    "chia/wallet/puzzles/custody/restrictions.py",
    "chia/wallet/puzzles/custody/send_message_banned.clsp",
    "chia/wallet/puzzles/load_clvm.py",
    "chia/wallet/puzzles/p2_conditions.py",
    "chia/wallet/puzzles/p2_delegated_conditions.py",
    "chia/wallet/puzzles/p2_delegated_puzzle.py",
    "chia/wallet/puzzles/p2_delegated_puzzle_or_hidden_puzzle.py",
    "chia/wallet/puzzles/p2_m_of_n_delegate_direct.py",
    "chia/wallet/puzzles/p2_puzzle_hash.py",
    "chia/wallet/puzzles/puzzle_utils.py",
    "chia/wallet/puzzles/singleton_top_layer.py",
    "chia/wallet/puzzles/singleton_top_layer_v1_1.py",
    "chia/wallet/puzzles/tails.py",
    "chia/wallet/puzzles/utility_macros.clib",
    "chia/wallet/remote_wallet/remote_coin_store.py",
    "chia/wallet/remote_wallet/remote_info.py",
    "chia/wallet/remote_wallet/remote_wallet.py",
    "chia/wallet/signer_protocol.py",
    "chia/wallet/singleton.py",
    "chia/wallet/singleton_record.py",
    "chia/wallet/trade_manager.py",
    "chia/wallet/trade_record.py",
    "chia/wallet/trading/offer.py",
    "chia/wallet/trading/trade_status.py",
    "chia/wallet/trading/trade_store.py",
    "chia/wallet/transaction_record.py",
    "chia/wallet/transaction_sorting.py",
    "chia/wallet/uncurried_puzzle.py",
    "chia/wallet/util/address_type.py",
    "chia/wallet/util/blind_signer_tl.py",
    "chia/wallet/util/clvm_streamable.py",
    "chia/wallet/util/compute_additions.py",
    "chia/wallet/util/compute_hints.py",
    "chia/wallet/util/compute_memos.py",
    "chia/wallet/util/curry_and_treehash.py",
    "chia/wallet/util/debug_spend_bundle.py",
    "chia/wallet/util/merkle_tree.py",
    "chia/wallet/util/merkle_utils.py",
    "chia/wallet/util/new_peak_queue.py",
    "chia/wallet/util/notifications.py",
    "chia/wallet/util/peer_request_cache.py",
    "chia/wallet/util/pprint.py",
    "chia/wallet/util/puzzle_compression.py",
    "chia/wallet/util/puzzle_decorator.py",
    "chia/wallet/util/puzzle_decorator_type.py",
    "chia/wallet/util/query_filter.py",
    "chia/wallet/util/signing.py",
    "chia/wallet/util/transaction_type.py",
    "chia/wallet/util/tx_config.py",
    "chia/wallet/util/wallet_sync_utils.py",
    "chia/wallet/util/wallet_types.py",
    "chia/wallet/vc_wallet/cr_cat_drivers.py",
    "chia/wallet/vc_wallet/cr_cat_wallet.py",
    "chia/wallet/vc_wallet/cr_outer_puzzle.py",
    "chia/wallet/vc_wallet/vc_drivers.py",
    "chia/wallet/vc_wallet/vc_store.py",
    "chia/wallet/vc_wallet/vc_wallet.py",
    "chia/wallet/wallet.py",
    "chia/wallet/wallet_action_scope.py",
    "chia/wallet/wallet_blockchain.py",
    "chia/wallet/wallet_coin_record.py",
    "chia/wallet/wallet_coin_store.py",
    "chia/wallet/wallet_info.py",
    "chia/wallet/wallet_interested_store.py",
    "chia/wallet/wallet_nft_store.py",
    "chia/wallet/wallet_node.py",
    "chia/wallet/wallet_node_api.py",
    "chia/wallet/wallet_pool_store.py",
    "chia/wallet/wallet_protocol.py",
    "chia/wallet/wallet_puzzle_store.py",
    "chia/wallet/wallet_request_types.py",
    "chia/wallet/wallet_retry_store.py",
    "chia/wallet/wallet_rpc_api.py",
    "chia/wallet/wallet_service.py",
    "chia/wallet/wallet_singleton_store.py",
    "chia/wallet/wallet_spend_bundle.py",
    "chia/wallet/wallet_state_manager.py",
    "chia/wallet/wallet_transaction_store.py",
    "chia/wallet/wallet_user_store.py",
    "chia/wallet/wallet_weight_proof_handler.py",
    "chia/wallet/wsm_apis.py",
]

target_scopes = [
    "Critical: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins",
    "Critical: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction",
    "High: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions",
    "High: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact",
    "High: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions",
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit + fuzzing questions for one Chia target.

    ```
    target_file format:
    "'File Name: chia/full_node/mempool_manager.py -> Scope: Critical: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction'"
    ```
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit and fuzzing questions for this exact Chia target:

    {target_file}

    Project context:
    Chia is a proof-of-space-and-time blockchain with a full node, wallet, farmer/harvester, timelord, pool wallet, Data Layer, CLVM puzzle stack, mempool, and peer-to-peer protocol surfaces. In-scope production logic includes consensus and block validation, spend bundle admission, wallet/state managers, singleton lineage, CAT/NFT/DID/VC flows, offers/trades, pool and farmer/harvester interactions, Data Layer stores, daemon/keychain/RPC boundaries, and protocol message handling.

    Core invariants:
    * XCH, CAT, NFT, DID, VC, pool, and singleton-controlled balances or ownership must remain conserved and authorization-bound.
    * Block validation, mempool admission, sync, weight proof handling, and protocol decoding must be deterministic across honest nodes.
    * Wallet, daemon, keychain, pool, and Data Layer operations must not let unprivileged actors sign, redirect rewards, mutate roots, or move coins they do not control.
    * Coin records, lineage proofs, puzzle hashes, spend conditions, offer settlement state, and Data Layer roots must remain canonical and unforgeable.

    Rules:
    * Treat `File Name:` as the exact file/module and `Scope:` as the only impact to target.
    * Assume full repo context is accessible; do not ask for code or say files are missing.
    * Generate 20 to 30 high-signal questions focused only on Critical or High impact.
    * At least 70% must be multi-step flow, invariant, fuzz, accounting, state-transition, or cross-module questions.
    * Every question must be testable by PoC, unit test, fuzz test, invariant test, differential test, or local integration test.
    * Avoid generic checklists, repeated root causes, best-practice items, and low/medium findings.
    * Do not generate resource-exhaustion questions unless the realistic result is consensus failure, invalid-chain acceptance, wallet corruption, or long-lived inability to process valid protocol actions.
    * Attacker is unprivileged: remote peer, spend-bundle submitter, wallet user, malicious CLVM/offer counterparty, pool participant, Data Layer client, or RPC caller operating within normal protocol rules.
    * Exclude leaked keys, farmer/validator host compromise, trusted key compromise, dependency compromise, local misconfiguration, phishing, malicious app changes, tests, mocks, generated files, scripts, and docs.

    High-value attack surfaces:
    * Spend bundle parsing, CLVM condition handling, puzzle reveal execution, coin announcement/assertion logic, and mempool conflict or replacement rules.
    * Block header/body validation, reward coin creation, fork handling, weight proof verification, sync state transitions, and protocol message decoding.
    * Wallet state manager flows for CAT/NFT/DID/VC/offer/clawback/pool/Data Layer state, singleton lineage, and cross-wallet settlement.
    * Daemon, keychain, RPC, and remote wallet boundaries around signing, key use, subscriptions, and privileged state mutation.
    * Farmer/harvester/pool/timelord interactions including partial proof handling, reward target enforcement, plot sync state, and pool singleton transitions.

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
    "[File: {target_file}] [Function: symbol_or_module] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: fuzz/state-test PARAMETERS and assert EXPECTED_PROPERTY.",
    ]
    """
    return prompt


def audit_format(question: str) -> str:
    """
    Generate a focused Chia exploit-question validation prompt.
    """
    return f"""# QUESTION SCAN PROMPT

## Exploit Question
{question}

## Scope Rules
- Audit only production Chia code in scope: consensus, full node, server, wallet, pools, Data Layer, daemon/keychain, farmer/harvester/timelord, protocol handlers, CLVM puzzle sources, and supporting types/utilities with direct protocol impact.
- Ignore tests, docs, mocks, generated files, scripts, local fixtures, vendored code, package metadata, and operator-only local setup unless the claim proves direct Critical/High chain impact.
- This protocol pays only High and Critical issues; reject low, medium, best-practice, and pure resource-exhaustion reports.

## Objective
Decide whether the question leads to a real, reachable Chia vulnerability.
The attacker must be unprivileged and enter through a spend bundle, block, protocol message, wallet or RPC request, pool/Data Layer action, or peer/mempool/sync path implemented in this repo.
Prefer #NoVulnerability unless the path is concrete, local-testable, and bounty-grade.

## Allowed Impact Scope
Only these impacts are valid:
- Critical: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Critical: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- High: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- High: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- High: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions

## Method
1. Trace the attacker-controlled entrypoint.
2. Map it to exact production Chia files/functions.
3. Check guards for signatures, puzzle/lineage validation, ownership, key authorization, spend conditions, coin accounting, protocol decoding, sync invariants, and deterministic execution.
4. Prove root cause with file/function/line references and a reproducible PoC or test plan.
5. Reject if existing validation prevents the exploit or the final impact is not one allowed High/Critical impact.

## Reject Immediately
- Requires leaked keys, validator/admin/gov compromise, trusted host compromise, dependency compromise, broken cryptography, phishing, malicious integrator behavior, or unsupported external assumptions.
- Only affects tests, docs, configs, scripts, mocks, generated code, local fixtures, CLI ergonomics, logs, observability, or non-security correctness.
- External dependency behavior is the only cause.
- Impact is only rejected tx, harmless revert, local misconfiguration, temporary spam, theoretical risk, or unbounded resource use without Critical/High protocol impact.

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
    Generate a short cross-project analog scan prompt for Chia.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Access Rules (Strict)
- Treat production Chia files in the provided scope as accessible context.
- Do not claim missing/inaccessible files.
- Do not scan tests, docs, build files, generated files, mocks, scripts, fixtures, vendored code, package metadata, or CLI-only behavior as audited targets.
- Only High and Critical protocol/security impacts are payable; do not report medium/low/resource-only analogs.

## Objective
Use the external report's vulnerability class only as a hint.
Find an analog only if Chia has its own reachable root cause in consensus, full node, wallet, CLVM puzzle, pool, Data Layer, daemon/keychain, RPC, or protocol-handling code.
The attacker must be unprivileged and the impact must match the allowed Chia impacts below.

## Allowed Impact Scope
Only these impacts are valid:
- Critical: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Critical: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- High: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- High: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- High: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions

## Method
1. Classify the external bug class: auth bypass, accounting bug, CLVM/puzzle flaw, consensus nondeterminism, protocol parsing bug, wallet settlement bug, pool/Data Layer bug, or state corruption.
2. Map only to exact Chia production files/functions.
3. Prove attacker path, missing/insufficient guard, and exact High/Critical impact.
4. Reject if Chia validation blocks it or the analogy is only superficial.

## Disqualify Immediately
- No reachable unprivileged entry path.
- Requires leaked keys, admin/gov/validator compromise, host compromise, dependency compromise, cryptographic break, or unsupported assumptions.
- Test/docs/config/build/generated/mock/local-only issue.
- Impact is temporary spam, logging, observability, CLI behavior, rejected tx, harmless revert, non-security correctness, or theory without protocol impact.

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
    Generate a strict Chia bounty-style validation prompt for security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim against Chia production code and SECURITY.md.
- Do not invent a new vulnerability or upgrade severity unless the evidence proves it.
- This protocol pays only High and Critical issues; reject low, medium, informational, best-practice, resource-only, and speculative reports.
- A valid report must be triggerable by an unprivileged spend-bundle submitter, remote peer, wallet or RPC caller, malicious CLVM/offer counterparty, pool participant, Data Layer client, or sync/mempool actor through code in this repo.
- Reject validator/farmer-key compromise, leaked keys, host compromise, dependency-only behavior, cryptographic breaks, phishing, victim mistakes, malicious integrator behavior, local misconfiguration, and unsupported protocol assumptions.

## In-Scope Protocol Areas
- Consensus and block validation, spend bundle admission, mempool/recheck behavior, sync/weight proof handling, and deterministic state transitions.
- Wallet, singleton, CAT/NFT/DID/VC, offer/trade, pool wallet, and Data Layer logic where direct High/Critical impact is proven.
- Daemon, keychain, RPC, remote wallet, farmer/harvester/timelord, and peer protocol handling when they enable a production exploit path.
- CLVM puzzle sources, lineage/ownership checks, reward handling, and supporting type/utility code used by production validation paths.
- Reject tests, docs, mocks, generated files, scripts, configs, local fixtures, vendored libraries, CLI-only behavior, and non-security correctness unless the claim proves direct High/Critical chain impact.

## Allowed Impact Scope
Only these impacts are valid:
- Critical: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Critical: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- High: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- High: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- High: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken authorization/accounting/state/consensus/IBC/EVM/precompile invariant.
3. Reachable exploit path: preconditions -> attacker action -> trigger -> bad result.
4. Existing guards reviewed and shown insufficient.
5. Concrete allowed High/Critical impact with realistic likelihood.
6. Reproducible proof path: unit PoC, deterministic integration test, invariant test, fuzz test, fork test, or exact local steps.
7. No rejection reason from SECURITY.md, privileges, scope exclusions, or known intended behavior.

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
[Concrete allowed Chia security impact and severity rationale]

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
