import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = "anza-xyz/agave"
# todo: the name of the repository
REPO_NAME = "agave"

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
    # SVM transaction lifecycle, fees, rent, and cost accounting
    # =================================================================================
    "builtins-default-costs/src/lib.rs",
    "compute-budget/src/compute_budget.rs",
    "compute-budget/src/compute_budget_limits.rs",
    "compute-budget/src/lib.rs",
    "compute-budget-instruction/src/builtin_programs_filter.rs",
    "compute-budget-instruction/src/compute_budget_instruction_details.rs",
    "compute-budget-instruction/src/compute_budget_program_id_filter.rs",
    "compute-budget-instruction/src/instructions_processor.rs",
    "compute-budget-instruction/src/lib.rs",
    "cost-model/src/block_cost_limits.rs",
    "cost-model/src/cost_model.rs",
    "cost-model/src/cost_tracker.rs",
    "cost-model/src/cost_tracker_post_analysis.rs",
    "cost-model/src/lib.rs",
    "cost-model/src/shred_limit.rs",
    "cost-model/src/transaction_cost.rs",
    "feature-set/src/lib.rs",
    "fee/src/lib.rs",
    "reserved-account-keys/src/lib.rs",
    "runtime-transaction/src/instruction_data_len.rs",
    "runtime-transaction/src/instruction_meta.rs",
    "runtime-transaction/src/lib.rs",
    "runtime-transaction/src/runtime_transaction/sdk_transactions.rs",
    "runtime-transaction/src/runtime_transaction/transaction_view.rs",
    "runtime-transaction/src/runtime_transaction.rs",
    "runtime-transaction/src/sanitize_config.rs",
    "runtime-transaction/src/signature_details.rs",
    "runtime-transaction/src/transaction_meta.rs",
    "runtime-transaction/src/transaction_with_meta.rs",
    "svm/src/account_loader.rs",
    "svm/src/account_overrides.rs",
    "svm/src/lib.rs",
    "svm/src/nonce_info.rs",
    "svm/src/program_loader.rs",
    "svm/src/rent_calculator.rs",
    "svm/src/rollback_accounts.rs",
    "svm/src/transaction_account_state_info.rs",
    "svm/src/transaction_balances.rs",
    "svm/src/transaction_commit_result.rs",
    "svm/src/transaction_error_metrics.rs",
    "svm/src/transaction_execution_result.rs",
    "svm/src/transaction_processing_callback.rs",
    "svm/src/transaction_processing_result.rs",
    "svm/src/transaction_processor.rs",
    "svm-callback/src/lib.rs",
    "svm-feature-set/src/lib.rs",
    "svm-log-collector/src/lib.rs",
    "svm-measure/src/lib.rs",
    "svm-measure/src/macros.rs",
    "svm-measure/src/measure.rs",
    "svm-timings/src/lib.rs",
    "svm-type-overrides/src/lib.rs",

    # =================================================================================
    # sBPF loader, invoke context, CPI, syscalls, and precompiles
    # =================================================================================
    "precompiles/src/ed25519.rs",
    "precompiles/src/lib.rs",
    "precompiles/src/secp256k1.rs",
    "precompiles/src/secp256r1.rs",
    "program-runtime/src/cpi.rs",
    "program-runtime/src/deploy.rs",
    "program-runtime/src/execution_budget.rs",
    "program-runtime/src/invoke_context.rs",
    "program-runtime/src/lib.rs",
    "program-runtime/src/loaded_programs.rs",
    "program-runtime/src/loading_task.rs",
    "program-runtime/src/mem_pool.rs",
    "program-runtime/src/memory.rs",
    "program-runtime/src/memory_context.rs",
    "program-runtime/src/program_cache_entry.rs",
    "program-runtime/src/program_metrics.rs",
    "program-runtime/src/serialization.rs",
    "program-runtime/src/stable_log.rs",
    "program-runtime/src/sysvar_cache.rs",
    "program-runtime/src/vm.rs",
    "syscalls/gen-syscall-list/src/main.rs",
    "syscalls/src/cpi.rs",
    "syscalls/src/lib.rs",
    "syscalls/src/logging.rs",
    "syscalls/src/mem_ops.rs",
    "syscalls/src/sysvar.rs",
    "transaction-context/src/instruction.rs",
    "transaction-context/src/instruction_accounts.rs",
    "transaction-context/src/lib.rs",
    "transaction-context/src/transaction.rs",
    "transaction-context/src/transaction_accounts.rs",
    "transaction-context/src/vm_addresses.rs",
    "transaction-context/src/vm_slice.rs",

    # =================================================================================
    # Bank, runtime state, and validator orchestration
    # =================================================================================
    "download-utils/src/lib.rs",
    "genesis/src/address_generator.rs",
    "genesis/src/genesis_accounts.rs",
    "genesis/src/lib.rs",
    "genesis/src/main.rs",
    "genesis/src/stakes.rs",
    "genesis/src/unlocks.rs",
    "genesis-utils/src/lib.rs",
    "genesis-utils/src/open.rs",
    "runtime/src/account_saver.rs",
    "runtime/src/accounts_background_service/pending_snapshot_packages.rs",
    "runtime/src/accounts_background_service/stats.rs",
    "runtime/src/accounts_background_service.rs",
    "runtime/src/bank/accounts_lt_hash.rs",
    "runtime/src/bank/address_lookup_table.rs",
    "runtime/src/bank/bank_hash_details.rs",
    "runtime/src/bank/builtins/core_bpf_migration/error.rs",
    "runtime/src/bank/builtins/core_bpf_migration/mod.rs",
    "runtime/src/bank/builtins/core_bpf_migration/source_buffer.rs",
    "runtime/src/bank/builtins/core_bpf_migration/target_bpf_v2.rs",
    "runtime/src/bank/builtins/core_bpf_migration/target_builtin.rs",
    "runtime/src/bank/builtins/core_bpf_migration/target_core_bpf.rs",
    "runtime/src/bank/builtins/mod.rs",
    "runtime/src/bank/check_transactions.rs",
    "runtime/src/bank/entry_bytes_budget.rs",
    "runtime/src/bank/fee_distribution.rs",
    "runtime/src/bank/metrics.rs",
    "runtime/src/bank/partitioned_epoch_rewards/calculation.rs",
    "runtime/src/bank/partitioned_epoch_rewards/distribution.rs",
    "runtime/src/bank/partitioned_epoch_rewards/epoch_rewards_hasher.rs",
    "runtime/src/bank/partitioned_epoch_rewards/mod.rs",
    "runtime/src/bank/partitioned_epoch_rewards/sysvar.rs",
    "runtime/src/bank/recent_blockhashes_account.rs",
    "runtime/src/bank/serde_snapshot.rs",
    "runtime/src/bank/sysvar_cache.rs",
    "runtime/src/bank.rs",
    "runtime/src/bank_forks.rs",
    "runtime/src/bank_forks_controller.rs",
    "runtime/src/bank_utils.rs",
    "runtime/src/commitment.rs",
    "runtime/src/dependency_tracker.rs",
    "runtime/src/epoch_stakes.rs",
    "runtime/src/genesis_utils.rs",
    "runtime/src/inflation_rewards/mod.rs",
    "runtime/src/inflation_rewards/points.rs",
    "runtime/src/installed_scheduler_pool.rs",
    "runtime/src/leader_schedule_utils.rs",
    "runtime/src/lib.rs",
    "runtime/src/non_circulating_supply.rs",
    "runtime/src/prioritization_fee.rs",
    "runtime/src/prioritization_fee_cache.rs",
    "runtime/src/read_optimized_dashmap.rs",
    "runtime/src/rent_collector.rs",
    "runtime/src/reward_info.rs",
    "runtime/src/runtime_config.rs",
    "runtime/src/serde_snapshot/obsolete_accounts.rs",
    "runtime/src/serde_snapshot/status_cache.rs",
    "runtime/src/serde_snapshot/storage.rs",
    "runtime/src/serde_snapshot/storages_list.rs",
    "runtime/src/serde_snapshot/types.rs",
    "runtime/src/serde_snapshot.rs",
    "runtime/src/slot_params.rs",
    "runtime/src/snapshot_bank_utils.rs",
    "runtime/src/snapshot_controller.rs",
    "runtime/src/snapshot_minimizer.rs",
    "runtime/src/snapshot_package/compare.rs",
    "runtime/src/snapshot_package.rs",
    "runtime/src/snapshot_utils/snapshot_storage_rebuilder.rs",
    "runtime/src/snapshot_utils.rs",
    "runtime/src/stake_account.rs",
    "runtime/src/stake_delegation.rs",
    "runtime/src/stake_history.rs",
    "runtime/src/stake_utils.rs",
    "runtime/src/stake_weighted_timestamp.rs",
    "runtime/src/stakes/serde_stakes.rs",
    "runtime/src/stakes.rs",
    "runtime/src/static_ids.rs",
    "runtime/src/status_cache.rs",
    "runtime/src/sysvar_account.rs",
    "runtime/src/transaction_balances.rs",
    "runtime/src/transaction_batch.rs",
    "runtime/src/transaction_execution.rs",
    "runtime/src/vote_sender_types.rs",
    "validator/src/admin_rpc_service.rs",
    "validator/src/bootstrap.rs",
    "validator/src/cli/thread_args.rs",
    "validator/src/cli.rs",
    "validator/src/commands/authorized_voter/mod.rs",
    "validator/src/commands/blockstore/mod.rs",
    "validator/src/commands/contact_info/mod.rs",
    "validator/src/commands/exit/mod.rs",
    "validator/src/commands/manage_block_production/mod.rs",
    "validator/src/commands/mod.rs",
    "validator/src/commands/monitor/mod.rs",
    "validator/src/commands/plugin/mod.rs",
    "validator/src/commands/repair_shred_from_peer/mod.rs",
    "validator/src/commands/repair_whitelist/mod.rs",
    "validator/src/commands/run/args/account_secondary_indexes.rs",
    "validator/src/commands/run/args/blockstore_options.rs",
    "validator/src/commands/run/args/json_rpc_config.rs",
    "validator/src/commands/run/args/pub_sub_config.rs",
    "validator/src/commands/run/args/rpc_bigtable_config.rs",
    "validator/src/commands/run/args/rpc_bootstrap_config.rs",
    "validator/src/commands/run/args/send_transaction_config.rs",
    "validator/src/commands/run/args.rs",
    "validator/src/commands/run/execute.rs",
    "validator/src/commands/run/mod.rs",
    "validator/src/commands/set_identity/mod.rs",
    "validator/src/commands/set_log_filter/mod.rs",
    "validator/src/commands/set_public_address/mod.rs",
    "validator/src/commands/staked_nodes_overrides/mod.rs",
    "validator/src/commands/wait_for_restart_window/mod.rs",
    "validator/src/dashboard.rs",
    "validator/src/lib.rs",
    "validator/src/main.rs",
    "version/src/client_ids.rs",
    "version/src/lib.rs",
    "version/src/v3.rs",
    "version/src/v4.rs",

    # =================================================================================
    # Native programs, stake, vote, and reward accounting
    # =================================================================================
    "builtins/src/core_bpf_migration.rs",
    "builtins/src/lib.rs",
    "builtins/src/prototype.rs",
    "leader-schedule/src/lib.rs",
    "leader-schedule/src/vote_keyed.rs",
    "programs/bpf_loader/src/lib.rs",
    "programs/compute-budget/src/lib.rs",
    "programs/system/src/lib.rs",
    "programs/system/src/system_instruction.rs",
    "programs/system/src/system_processor.rs",
    "programs/vote/src/lib.rs",
    "programs/vote/src/vote_processor.rs",
    "programs/vote/src/vote_state/handler.rs",
    "programs/vote/src/vote_state/mod.rs",
    "programs/zk-elgamal-proof/src/lib.rs",
    "programs/zk-token-proof/src/lib.rs",
    "vote/src/lib.rs",
    "vote/src/vote_account.rs",
    "vote/src/vote_parser.rs",
    "vote/src/vote_state_view/field_frames.rs",
    "vote/src/vote_state_view/frame_v1_14_11.rs",
    "vote/src/vote_state_view/frame_v3.rs",
    "vote/src/vote_state_view/frame_v4.rs",
    "vote/src/vote_state_view/list_view.rs",
    "vote/src/vote_state_view.rs",
    "vote/src/vote_transaction.rs",

    # =================================================================================
    # AccountsDB, account hashing, and snapshot state
    # =================================================================================
    "accounts-db/src/account_info.rs",
    "accounts-db/src/account_locks.rs",
    "accounts-db/src/account_storage/stored_account_info.rs",
    "accounts-db/src/account_storage.rs",
    "accounts-db/src/account_storage_entry.rs",
    "accounts-db/src/account_storage_reader.rs",
    "accounts-db/src/accounts.rs",
    "accounts-db/src/accounts_cache.rs",
    "accounts-db/src/accounts_db/accounts_db_config.rs",
    "accounts-db/src/accounts_db/stats.rs",
    "accounts-db/src/accounts_db.rs",
    "accounts-db/src/accounts_file.rs",
    "accounts-db/src/accounts_hash.rs",
    "accounts-db/src/accounts_index/account_map_entry.rs",
    "accounts-db/src/accounts_index/accounts_index_storage.rs",
    "accounts-db/src/accounts_index/bucket_map_holder.rs",
    "accounts-db/src/accounts_index/in_mem_accounts_index.rs",
    "accounts-db/src/accounts_index/iter.rs",
    "accounts-db/src/accounts_index/secondary.rs",
    "accounts-db/src/accounts_index/stats.rs",
    "accounts-db/src/accounts_index.rs",
    "accounts-db/src/accounts_scan.rs",
    "accounts-db/src/accounts_update_notifier_interface.rs",
    "accounts-db/src/active_stats.rs",
    "accounts-db/src/ancestors.rs",
    "accounts-db/src/ancient_append_vecs.rs",
    "accounts-db/src/append_vec/meta.rs",
    "accounts-db/src/append_vec.rs",
    "accounts-db/src/blockhash_queue.rs",
    "accounts-db/src/contains.rs",
    "accounts-db/src/is_loadable.rs",
    "accounts-db/src/is_zero_lamport.rs",
    "accounts-db/src/lib.rs",
    "accounts-db/src/obsolete_accounts.rs",
    "accounts-db/src/partitioned_rewards.rs",
    "accounts-db/src/pubkey_bins.rs",
    "accounts-db/src/read_only_accounts_cache.rs",
    "accounts-db/src/rolling_bit_field/iterators.rs",
    "accounts-db/src/rolling_bit_field.rs",
    "accounts-db/src/sorted_storages.rs",
    "accounts-db/src/stake_rewards.rs",
    "accounts-db/src/storable_accounts.rs",
    "accounts-db/src/utils.rs",
    "accounts-db/src/waitable_condvar.rs",
    "accounts-db/store-histogram/src/main.rs",
    "accounts-db/store-tool/src/main.rs",
    "bloom/src/bloom.rs",
    "bloom/src/lib.rs",
    "bucket_map/src/bucket.rs",
    "bucket_map/src/bucket_api.rs",
    "bucket_map/src/bucket_item.rs",
    "bucket_map/src/bucket_map.rs",
    "bucket_map/src/bucket_stats.rs",
    "bucket_map/src/bucket_storage.rs",
    "bucket_map/src/index_entry.rs",
    "bucket_map/src/lib.rs",
    "bucket_map/src/restart.rs",
    "fs/src/buffered_reader.rs",
    "fs/src/buffered_writer.rs",
    "fs/src/dirs.rs",
    "fs/src/file_info.rs",
    "fs/src/file_io.rs",
    "fs/src/io_setup.rs",
    "fs/src/io_uring/dir_remover.rs",
    "fs/src/io_uring/file_creator.rs",
    "fs/src/io_uring/file_writer.rs",
    "fs/src/io_uring/memory.rs",
    "fs/src/io_uring/mod.rs",
    "fs/src/io_uring/sequential_file_reader.rs",
    "fs/src/io_uring/sqpoll.rs",
    "fs/src/lib.rs",
    "fs/src/metadata.rs",
    "io-uring/src/lib.rs",
    "io-uring/src/ring.rs",
    "io-uring/src/slab.rs",
    "lattice-hash/src/lib.rs",
    "lattice-hash/src/lt_hash.rs",
    "merkle-tree/src/lib.rs",
    "merkle-tree/src/merkle_tree.rs",

    # =================================================================================
    # Public ingress, sigverify, banking stage, scheduling, and PoH
    # =================================================================================
    "banking-stage-ingress-types/src/lib.rs",
    "connection-cache/src/client_connection.rs",
    "connection-cache/src/connection_cache.rs",
    "connection-cache/src/connection_cache_stats.rs",
    "connection-cache/src/lib.rs",
    "connection-cache/src/nonblocking/client_connection.rs",
    "connection-cache/src/nonblocking/mod.rs",
    "entry/src/block_component.rs",
    "entry/src/entry.rs",
    "entry/src/entry_or_marker.rs",
    "entry/src/lib.rs",
    "entry/src/poh.rs",
    "net-utils/src/banlist.rs",
    "net-utils/src/ip_echo_client.rs",
    "net-utils/src/ip_echo_server.rs",
    "net-utils/src/lib.rs",
    "net-utils/src/multihomed_sockets.rs",
    "net-utils/src/pinned_xdp_sender.rs",
    "net-utils/src/socket_addr_space.rs",
    "net-utils/src/sockets.rs",
    "net-utils/src/token_bucket.rs",
    "perf/src/data_budget.rs",
    "perf/src/deduper.rs",
    "perf/src/lib.rs",
    "perf/src/packet.rs",
    "perf/src/recycled_vec.rs",
    "perf/src/recycler.rs",
    "perf/src/sigverify.rs",
    "perf/src/thread.rs",
    "poh/src/lib.rs",
    "poh/src/poh_controller.rs",
    "poh/src/poh_recorder.rs",
    "poh/src/poh_service.rs",
    "poh/src/record_channels.rs",
    "poh/src/transaction_recorder.rs",
    "quic-client/src/lib.rs",
    "quic-client/src/nonblocking/mod.rs",
    "quic-client/src/nonblocking/quic_client.rs",
    "quic-client/src/quic_client.rs",
    "scheduling-utils/src/error.rs",
    "scheduling-utils/src/lib.rs",
    "scheduling-utils/src/pubkeys_ptr.rs",
    "scheduling-utils/src/responses_region.rs",
    "scheduling-utils/src/thread_aware_account_locks.rs",
    "scheduling-utils/src/transaction_ptr.rs",
    "streamer/src/evicting_sender.rs",
    "streamer/src/lib.rs",
    "streamer/src/msghdr.rs",
    "streamer/src/nonblocking/connection_rate_limiter.rs",
    "streamer/src/nonblocking/mod.rs",
    "streamer/src/nonblocking/qos.rs",
    "streamer/src/nonblocking/quic.rs",
    "streamer/src/nonblocking/simple_qos.rs",
    "streamer/src/nonblocking/stream_throttle.rs",
    "streamer/src/nonblocking/swqos.rs",
    "streamer/src/packet.rs",
    "streamer/src/quic.rs",
    "streamer/src/quic_socket.rs",
    "streamer/src/recvmmsg.rs",
    "streamer/src/sendmmsg.rs",
    "streamer/src/streamer.rs",
    "tls-utils/src/config.rs",
    "tls-utils/src/crypto_provider.rs",
    "tls-utils/src/lib.rs",
    "tls-utils/src/notify_key_update.rs",
    "tls-utils/src/quic_client_certificate.rs",
    "tls-utils/src/skip_client_verification.rs",
    "tls-utils/src/skip_server_verification.rs",
    "tls-utils/src/tls_certificates.rs",
    "tpu-client/src/lib.rs",
    "tpu-client/src/nonblocking/mod.rs",
    "tpu-client/src/nonblocking/tpu_client.rs",
    "tpu-client/src/tpu_client.rs",
    "tpu-client-next/src/client_builder.rs",
    "tpu-client-next/src/connection_worker.rs",
    "tpu-client-next/src/connection_workers_scheduler.rs",
    "tpu-client-next/src/leader_updater.rs",
    "tpu-client-next/src/lib.rs",
    "tpu-client-next/src/logging.rs",
    "tpu-client-next/src/metrics.rs",
    "tpu-client-next/src/node_address_service/leader_tpu_cache_service.rs",
    "tpu-client-next/src/node_address_service/recent_leader_slots.rs",
    "tpu-client-next/src/node_address_service/slot_event.rs",
    "tpu-client-next/src/node_address_service/slot_receiver.rs",
    "tpu-client-next/src/node_address_service/slot_update_service.rs",
    "tpu-client-next/src/node_address_service.rs",
    "tpu-client-next/src/quic_networking/error.rs",
    "tpu-client-next/src/quic_networking.rs",
    "tpu-client-next/src/send_transaction_stats.rs",
    "tpu-client-next/src/websocket_node_address_service.rs",
    "tpu-client-next/src/workers_cache.rs",
    "udp-client/src/lib.rs",
    "udp-client/src/nonblocking/mod.rs",
    "udp-client/src/nonblocking/udp_client.rs",
    "udp-client/src/udp_client.rs",
    "unified-scheduler-logic/src/lib.rs",
    "unified-scheduler-pool/src/lib.rs",
    "xdp/src/device.rs",
    "xdp/src/ecn_codepoint.rs",
    "xdp/src/gre/mod.rs",
    "xdp/src/gre/packet.rs",
    "xdp/src/lib.rs",
    "xdp/src/lpm.rs",
    "xdp/src/netlink.rs",
    "xdp/src/packet.rs",
    "xdp/src/program.rs",
    "xdp/src/route.rs",
    "xdp/src/route_monitor.rs",
    "xdp/src/socket.rs",
    "xdp/src/transmitter.rs",
    "xdp/src/tx_loop.rs",
    "xdp/src/umem.rs",
    "xdp-ebpf/src/bin/agave-xdp-prog.rs",
    "xdp-ebpf/src/lib.rs",

    # =================================================================================
    # RPC, pubsub, transaction status, and account decoding
    # =================================================================================
    "account-decoder/src/lib.rs",
    "account-decoder/src/parse_account_data.rs",
    "account-decoder/src/parse_address_lookup_table.rs",
    "account-decoder/src/parse_bpf_loader.rs",
    "account-decoder/src/parse_config.rs",
    "account-decoder/src/parse_nonce.rs",
    "account-decoder/src/parse_stake.rs",
    "account-decoder/src/parse_sysvar.rs",
    "account-decoder/src/parse_token.rs",
    "account-decoder/src/parse_token_extension.rs",
    "account-decoder/src/parse_vote.rs",
    "account-decoder/src/validator_info.rs",
    "account-decoder-client-types/src/lib.rs",
    "account-decoder-client-types/src/token.rs",
    "banks-client/src/error.rs",
    "banks-client/src/lib.rs",
    "banks-interface/src/lib.rs",
    "banks-server/src/banks_server.rs",
    "banks-server/src/lib.rs",
    "pubsub-client/src/lib.rs",
    "pubsub-client/src/nonblocking/mod.rs",
    "pubsub-client/src/nonblocking/pubsub_client.rs",
    "pubsub-client/src/pubsub_client.rs",
    "rpc/src/cluster_tpu_info.rs",
    "rpc/src/filter.rs",
    "rpc/src/lib.rs",
    "rpc/src/max_slots.rs",
    "rpc/src/optimistically_confirmed_bank_tracker.rs",
    "rpc/src/parsed_token_accounts.rs",
    "rpc/src/rpc/account_resolver.rs",
    "rpc/src/rpc.rs",
    "rpc/src/rpc_cache.rs",
    "rpc/src/rpc_completed_slots_service.rs",
    "rpc/src/rpc_health.rs",
    "rpc/src/rpc_pubsub.rs",
    "rpc/src/rpc_pubsub_service.rs",
    "rpc/src/rpc_service.rs",
    "rpc/src/rpc_subscription_tracker.rs",
    "rpc/src/rpc_subscriptions.rs",
    "rpc/src/slot_status_notifier.rs",
    "rpc/src/transaction_notifier_interface.rs",
    "rpc/src/transaction_status_service.rs",
    "rpc-client/src/http_sender.rs",
    "rpc-client/src/lib.rs",
    "rpc-client/src/nonblocking/mod.rs",
    "rpc-client/src/nonblocking/rpc_client.rs",
    "rpc-client/src/rpc_client.rs",
    "rpc-client/src/rpc_sender.rs",
    "rpc-client/src/spinner.rs",
    "rpc-client-api/src/client_error.rs",
    "rpc-client-api/src/custom_error.rs",
    "rpc-client-api/src/lib.rs",
    "rpc-client-api/src/response.rs",
    "rpc-client-nonce-utils/src/blockhash_query.rs",
    "rpc-client-nonce-utils/src/lib.rs",
    "rpc-client-nonce-utils/src/nonblocking/blockhash_query.rs",
    "rpc-client-nonce-utils/src/nonblocking/mod.rs",
    "rpc-client-types/src/config.rs",
    "rpc-client-types/src/error_object.rs",
    "rpc-client-types/src/filter.rs",
    "rpc-client-types/src/lib.rs",
    "rpc-client-types/src/request.rs",
    "rpc-client-types/src/response.rs",
    "send-transaction-service/src/lib.rs",
    "send-transaction-service/src/send_transaction_service.rs",
    "send-transaction-service/src/send_transaction_service_stats.rs",
    "send-transaction-service/src/tpu_info.rs",
    "send-transaction-service/src/transaction_client.rs",
    "storage-bigtable/build-proto/src/main.rs",
    "storage-bigtable/proto/google.api.rs",
    "storage-bigtable/proto/google.bigtable.v2.rs",
    "storage-bigtable/proto/google.protobuf.rs",
    "storage-bigtable/proto/google.r#type.rs",
    "storage-bigtable/proto/google.rpc.rs",
    "storage-bigtable/src/access_token.rs",
    "storage-bigtable/src/bigtable.rs",
    "storage-bigtable/src/compression.rs",
    "storage-bigtable/src/lib.rs",
    "storage-bigtable/src/root_ca_certificate.rs",
    "storage-proto/src/convert.rs",
    "storage-proto/src/lib.rs",
    "transaction-status/src/extract_memos.rs",
    "transaction-status/src/lib.rs",
    "transaction-status/src/parse_accounts.rs",
    "transaction-status/src/parse_address_lookup_table.rs",
    "transaction-status/src/parse_associated_token.rs",
    "transaction-status/src/parse_bpf_loader.rs",
    "transaction-status/src/parse_instruction.rs",
    "transaction-status/src/parse_stake.rs",
    "transaction-status/src/parse_system.rs",
    "transaction-status/src/parse_token/extension/confidential_mint_burn.rs",
    "transaction-status/src/parse_token/extension/confidential_transfer.rs",
    "transaction-status/src/parse_token/extension/confidential_transfer_fee.rs",
    "transaction-status/src/parse_token/extension/cpi_guard.rs",
    "transaction-status/src/parse_token/extension/default_account_state.rs",
    "transaction-status/src/parse_token/extension/group_member_pointer.rs",
    "transaction-status/src/parse_token/extension/group_pointer.rs",
    "transaction-status/src/parse_token/extension/interest_bearing_mint.rs",
    "transaction-status/src/parse_token/extension/memo_transfer.rs",
    "transaction-status/src/parse_token/extension/metadata_pointer.rs",
    "transaction-status/src/parse_token/extension/mint_close_authority.rs",
    "transaction-status/src/parse_token/extension/mod.rs",
    "transaction-status/src/parse_token/extension/pausable.rs",
    "transaction-status/src/parse_token/extension/permanent_delegate.rs",
    "transaction-status/src/parse_token/extension/permissioned_burn.rs",
    "transaction-status/src/parse_token/extension/reallocate.rs",
    "transaction-status/src/parse_token/extension/scaled_ui_amount.rs",
    "transaction-status/src/parse_token/extension/token_group.rs",
    "transaction-status/src/parse_token/extension/token_metadata.rs",
    "transaction-status/src/parse_token/extension/transfer_fee.rs",
    "transaction-status/src/parse_token/extension/transfer_hook.rs",
    "transaction-status/src/parse_token.rs",
    "transaction-status/src/parse_vote.rs",
    "transaction-status/src/token_balances.rs",
    "transaction-status-client-types/src/lib.rs",
    "transaction-status-client-types/src/option_serializer.rs",

    # =================================================================================
    # Consensus, replay, gossip, turbine, and ledger
    # =================================================================================
    "core/src/admin_rpc_post_init.rs",
    "core/src/banking_stage/committer.rs",
    "core/src/banking_stage/consume_worker.rs",
    "core/src/banking_stage/consumer.rs",
    "core/src/banking_stage/decision_maker.rs",
    "core/src/banking_stage/latest_validator_vote_packet.rs",
    "core/src/banking_stage/leader_slot_metrics.rs",
    "core/src/banking_stage/leader_slot_timing_metrics.rs",
    "core/src/banking_stage/progress_tracker.rs",
    "core/src/banking_stage/scheduler_messages.rs",
    "core/src/banking_stage/tpu_to_pack.rs",
    "core/src/banking_stage/transaction_scheduler/batch_id_generator.rs",
    "core/src/banking_stage/transaction_scheduler/greedy_scheduler.rs",
    "core/src/banking_stage/transaction_scheduler/in_flight_tracker.rs",
    "core/src/banking_stage/transaction_scheduler/mod.rs",
    "core/src/banking_stage/transaction_scheduler/receive_and_buffer.rs",
    "core/src/banking_stage/transaction_scheduler/scheduler.rs",
    "core/src/banking_stage/transaction_scheduler/scheduler_common.rs",
    "core/src/banking_stage/transaction_scheduler/scheduler_controller.rs",
    "core/src/banking_stage/transaction_scheduler/scheduler_error.rs",
    "core/src/banking_stage/transaction_scheduler/scheduler_metrics.rs",
    "core/src/banking_stage/transaction_scheduler/transaction_priority_id.rs",
    "core/src/banking_stage/transaction_scheduler/transaction_state.rs",
    "core/src/banking_stage/transaction_scheduler/transaction_state_container.rs",
    "core/src/banking_stage/vote_packet_receiver.rs",
    "core/src/banking_stage/vote_storage.rs",
    "core/src/banking_stage/vote_worker.rs",
    "core/src/banking_stage.rs",
    "core/src/banking_trace.rs",
    "core/src/cluster_info_vote_listener.rs",
    "core/src/cluster_slots_service/cluster_slots.rs",
    "core/src/cluster_slots_service/slot_supporters.rs",
    "core/src/cluster_slots_service.rs",
    "core/src/commitment_service.rs",
    "core/src/completed_data_sets_service.rs",
    "core/src/consensus/fork_choice.rs",
    "core/src/consensus/heaviest_subtree_fork_choice.rs",
    "core/src/consensus/latest_validator_votes_for_frozen_banks.rs",
    "core/src/consensus/progress_map.rs",
    "core/src/consensus/tower1_14_11.rs",
    "core/src/consensus/tower1_7_14.rs",
    "core/src/consensus/tower_storage.rs",
    "core/src/consensus/tower_vote_state.rs",
    "core/src/consensus/tree_diff.rs",
    "core/src/consensus/vote_stake_tracker.rs",
    "core/src/consensus.rs",
    "core/src/cost_update_service.rs",
    "core/src/drop_bank_service.rs",
    "core/src/epoch_specs.rs",
    "core/src/fetch_stage.rs",
    "core/src/forwarding_stage/packet_container.rs",
    "core/src/forwarding_stage.rs",
    "core/src/gen_keys.rs",
    "core/src/lib.rs",
    "core/src/next_leader.rs",
    "core/src/optimistic_confirmation_verifier.rs",
    "core/src/repair/ancestor_hashes_service.rs",
    "core/src/repair/block_id_repair_service/stats.rs",
    "core/src/repair/block_id_repair_service.rs",
    "core/src/repair/cluster_slot_state_verifier.rs",
    "core/src/repair/duplicate_repair_status.rs",
    "core/src/repair/malicious_repair_handler.rs",
    "core/src/repair/mod.rs",
    "core/src/repair/outstanding_requests.rs",
    "core/src/repair/packet_threshold.rs",
    "core/src/repair/repair_generic_traversal.rs",
    "core/src/repair/repair_handler.rs",
    "core/src/repair/repair_response.rs",
    "core/src/repair/repair_service.rs",
    "core/src/repair/repair_weight.rs",
    "core/src/repair/repair_weighted_traversal.rs",
    "core/src/repair/request_response.rs",
    "core/src/repair/result.rs",
    "core/src/repair/serve_repair.rs",
    "core/src/repair/serve_repair_service.rs",
    "core/src/repair/standard_repair_handler.rs",
    "core/src/replay_stage/dead_slots.rs",
    "core/src/replay_stage/update_parent.rs",
    "core/src/replay_stage.rs",
    "core/src/resource_limits.rs",
    "core/src/result.rs",
    "core/src/sample_performance_service.rs",
    "core/src/scheduler_bindings_server.rs",
    "core/src/shred_fetch_stage.rs",
    "core/src/sigverify.rs",
    "core/src/sigverify_stage.rs",
    "core/src/snapshot_packager_service/snapshot_gossip_manager.rs",
    "core/src/snapshot_packager_service.rs",
    "core/src/staked_nodes_updater_service.rs",
    "core/src/stats_reporter_service.rs",
    "core/src/system_monitor_service.rs",
    "core/src/tpu.rs",
    "core/src/tpu_entry_notifier.rs",
    "core/src/transaction_priority.rs",
    "core/src/tvu.rs",
    "core/src/unfrozen_gossip_verified_vote_hashes.rs",
    "core/src/validator.rs",
    "core/src/voting_service.rs",
    "core/src/warm_quic_cache_service.rs",
    "core/src/window_service.rs",
    "gossip/src/cluster_info.rs",
    "gossip/src/cluster_info_metrics.rs",
    "gossip/src/contact_info.rs",
    "gossip/src/contact_info_notifier.rs",
    "gossip/src/crds.rs",
    "gossip/src/crds_data.rs",
    "gossip/src/crds_entry.rs",
    "gossip/src/crds_filter.rs",
    "gossip/src/crds_gossip.rs",
    "gossip/src/crds_gossip_error.rs",
    "gossip/src/crds_gossip_pull.rs",
    "gossip/src/crds_gossip_push.rs",
    "gossip/src/crds_shards.rs",
    "gossip/src/crds_value.rs",
    "gossip/src/duplicate_shred.rs",
    "gossip/src/duplicate_shred_handler.rs",
    "gossip/src/duplicate_shred_listener.rs",
    "gossip/src/epoch_slots.rs",
    "gossip/src/epoch_specs.rs",
    "gossip/src/gossip_error.rs",
    "gossip/src/gossip_service.rs",
    "gossip/src/harness.rs",
    "gossip/src/lib.rs",
    "gossip/src/node.rs",
    "gossip/src/ping_pong.rs",
    "gossip/src/protocol.rs",
    "gossip/src/push_active_set.rs",
    "gossip/src/received_cache.rs",
    "gossip/src/restart_crds_values.rs",
    "gossip/src/sigverify_cache.rs",
    "gossip/src/tlv.rs",
    "gossip/src/weighted_shuffle.rs",
    "ledger/src/ancestor_iterator.rs",
    "ledger/src/bank_forks_utils.rs",
    "ledger/src/bigtable_delete.rs",
    "ledger/src/bigtable_upload.rs",
    "ledger/src/bigtable_upload_service.rs",
    "ledger/src/bit_vec.rs",
    "ledger/src/block_error.rs",
    "ledger/src/blockstore/blockstore_purge.rs",
    "ledger/src/blockstore/cleanup_service.rs",
    "ledger/src/blockstore/column.rs",
    "ledger/src/blockstore/error.rs",
    "ledger/src/blockstore.rs",
    "ledger/src/blockstore_db.rs",
    "ledger/src/blockstore_meta.rs",
    "ledger/src/blockstore_metric_report_service.rs",
    "ledger/src/blockstore_metrics.rs",
    "ledger/src/blockstore_options.rs",
    "ledger/src/blockstore_processor.rs",
    "ledger/src/deshred_transaction_notifier_interface.rs",
    "ledger/src/entry_notifier_interface.rs",
    "ledger/src/entry_notifier_service.rs",
    "ledger/src/genesis_utils.rs",
    "ledger/src/leader_schedule_cache.rs",
    "ledger/src/lib.rs",
    "ledger/src/next_slots_iterator.rs",
    "ledger/src/rooted_slot_iterator.rs",
    "ledger/src/shred/common.rs",
    "ledger/src/shred/filter.rs",
    "ledger/src/shred/merkle.rs",
    "ledger/src/shred/merkle_tree.rs",
    "ledger/src/shred/payload.rs",
    "ledger/src/shred/shred_code.rs",
    "ledger/src/shred/shred_data.rs",
    "ledger/src/shred/stats.rs",
    "ledger/src/shred/traits.rs",
    "ledger/src/shred/wire.rs",
    "ledger/src/shred.rs",
    "ledger/src/shredder.rs",
    "ledger/src/sigverify_shreds.rs",
    "ledger/src/slot_stats.rs",
    "ledger/src/staking_utils.rs",
    "ledger/src/transaction_address_lookup_table_scanner.rs",
    "ledger/src/use_snapshot_archives_at_startup.rs",
    "turbine/src/addr_cache.rs",
    "turbine/src/broadcast_stage/broadcast_duplicates_run.rs",
    "turbine/src/broadcast_stage/broadcast_metrics.rs",
    "turbine/src/broadcast_stage/broadcast_utils.rs",
    "turbine/src/broadcast_stage/standard_broadcast_run.rs",
    "turbine/src/broadcast_stage.rs",
    "turbine/src/cluster_nodes.rs",
    "turbine/src/lib.rs",
    "turbine/src/retransmit_stage.rs",
    "turbine/src/sigverify_shreds.rs",

    # =================================================================================
    # Shared support primitives
    # =================================================================================
    "cpu-utils/src/affinity.rs",
    "cpu-utils/src/lib.rs",
    "logger/src/lib.rs",
    "math-utils/src/lib.rs",
    "math-utils/src/welford_stats.rs",
    "measure/src/lib.rs",
    "measure/src/macros.rs",
    "measure/src/measure.rs",
    "notifier/src/lib.rs",
    "random/src/lib.rs",
    "random/src/range.rs",
    "random/src/weighted.rs",
    "rayon-threadlimit/src/lib.rs",

]


target_scopes = [
    "Critical. An unprivileged attacker can craft a transaction whose fee, rent, rollback, or balance-commit accounting in the SVM lifecycle moves, mints, duplicates, or destroys lamports the signer does not own.",
    "Critical. An unprivileged attacker can submit a transaction whose loading, sanitization, ALT resolution, or execution result differs between honest validators, causing bank-hash divergence, a fork, or an unbootable ledger replay.",
    "Critical. An unprivileged attacker can replay or double-apply one signed transaction through durable-nonce advance, blockhash-queue aging, or status-cache dedup so a single authorization settles more than once.",
    "Critical. An unprivileged attacker can send a valid-looking transaction that panics, overflows, aborts, or wedges banking/replay on every node, halting consensus until human intervention.",
    "High. An unprivileged attacker can bypass account-lock, reserved-key, writable-declaration, or loaded-accounts-data-size limits and write to or read state the transaction never declared or paid for.",
    "High. An unprivileged attacker can make compute-budget, cost-model, or fee accounting charge materially less than the real CPU, memory, or account-load work performed, exhausting block capacity or node resources below true cost.",
]


scope_scan = [
]
def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one agave target.

    ```
    target_file format:
    "'File Name: builtins-default-costs/src/lib.rs -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit and fuzzing questions for this exact agave target:

    {target_file}

    Project focus:
    These crates implement the Agave SVM transaction lifecycle: sanitization and metadata, account loading and locks, compute-budget and cost-model accounting, fee and rent collection, durable-nonce and blockhash replay protection, and commit of balances back to the bank. The bounty focus is loss of funds, consensus divergence, halts, and underpriced work reachable from an ordinary transaction.

    Rules:
    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Rust symbols when possible.
    * Attacker is unprivileged only: a normal user broadcasting transactions (any instruction mix, ALTs, durable nonces, compute-budget instructions, arbitrary account lists) to a public TPU or RPC endpoint.
    * Never assume validator, leader, staked-node, peer, gossip, shred-sender, RPC-operator, genesis, CLI, or config control, and never assume leaked keys or local filesystem access.
    * Do not rely on mocked paths, handcrafted internal helpers, direct store mutation, feature-gate flips, or off-repo assumptions.
    * Out of scope per SECURITY.md: dependencies and the sBPF interpreter, metrics, Geyser and `scheduler-bindings` external processes, Alpenglow/votor crates and plumbing, Loader V4 paths, maliciously crafted snapshots, bootstrap-phase-only issues fixable by config, and RPC DoS needing more than one call per `CLUSTER_SLOT_TIME_TARGET / 2`, multiple clients, or unfiltered getProgramAccounts without secondary indexes.
    * Generate 12 to 18 high-signal questions.
    * At least 70% must be multi-step fee/rent accounting, replay, deterministic-execution, account-privilege, or cost-accounting questions.
    * Every question must be testable by unit test, integration test, fuzz test, invariant test, or differential test.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Lamports and account data are conserved: no transaction path creates, destroys, or moves value the signer did not authorize.
    * A transaction is charged exactly once, and fee payer debit, rollback, and refund stay consistent whether execution succeeds or fails.
    * One signed message settles exactly once: blockhash aging, nonce advance, and status-cache dedup must never allow a second commit.
    * Loading, sanitization, budget, rent, and commit must be deterministic for identical input and feature set across all honest nodes.
    * Only accounts declared writable and unlocked by the message may be mutated; reserved keys stay read-only.
    * Declared compute units, loaded-accounts-data-size, and cost-model estimates must upper-bound the real work performed.

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
    "[File: {target_file}] [Function: symbol_or_module] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: test/fuzz PARAMETERS and assert VALUE_CONSERVATION, ONE_TIME_SETTLEMENT, DETERMINISM, or COST_UPPER_BOUND.",
    ]
    """
    return prompt

def audit_format(security_question: str) -> str:
    """
    Generate a focused agave exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: a normal user broadcasting transactions (any instruction mix, ALTs, durable nonces, compute-budget instructions, arbitrary account lists) to a public TPU or RPC endpoint.
- Reject anything requiring validator/leader/peer/gossip/staked-node control, operator config, leaked keys, mocked paths, direct store mutation, or best-practice cleanup.
- Out of scope per SECURITY.md: dependencies and the sBPF interpreter, metrics, Geyser and `scheduler-bindings` external processes, Alpenglow/votor crates and plumbing, Loader V4 paths, maliciously crafted snapshots, bootstrap-phase-only issues fixable by config, and RPC DoS needing more than one call per `CLUSTER_SLOT_TIME_TARGET / 2`, multiple clients, or unfiltered getProgramAccounts without secondary indexes.

## Validate
- Trace the exact reachable Rust path from the attacker entrypoint into loading, budget, fee, rent, replay, or commit logic.
- Check whether existing sanitization, lock, signature, nonce, status-cache, budget, or rent guards already stop it.
- Accept only real value loss/creation, double settlement, cross-node divergence or halt, undeclared account mutation, or materially underpriced execution.
- Require exact file/function support and a reproducible Rust unit/integration/fuzz/invariant PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker inputs, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact and matching Agave bounty category]

### Likelihood Explanation
[Preconditions, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Rust unit/integration test or fuzz/invariant test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for agave security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Reject validator-only, leader-only, peer-only, gossip-only, operator-config, leaked-key, metrics, dependency, docs/style, mocked-path, and purely theoretical issues.
- Reject if the exploit needs unrealistic assumptions, victim mistakes, direct store mutation, or unsupported protocol behavior.
- Out of scope per SECURITY.md: dependencies and the sBPF interpreter, metrics, Geyser and `scheduler-bindings` external processes, Alpenglow/votor crates and plumbing, Loader V4 paths, maliciously crafted snapshots, bootstrap-phase-only issues fixable by config, and RPC DoS needing more than one call per `CLUSTER_SLOT_TIME_TARGET / 2`, multiple clients, or unfiltered getProgramAccounts without secondary indexes.
- Reject if the bug was fixed, acknowledged, or publicly disclosed already, per the eligibility rules.
- A valid report must be triggerable by an unprivileged user, unless the claim proves privilege escalation from an unprivileged path.
- The final impact must map to an Agave bounty category: Loss of Funds, Consensus/Safety Violation, Liveness, DoS, or RPC.
- Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken security/accounting assumption.
3. Reachable exploit path: preconditions -> attacker action -> trigger -> bad result.
4. Existing checks/guards reviewed and shown insufficient.
5. Concrete in-scope impact with realistic likelihood.
6. Reproducible proof path: unit PoC, integration test, invariant/fuzz test, or exact manual steps.
7. No obvious rejection reason from SECURITY.md, known issues, privileges, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can a normal external user trigger this by broadcasting a single ordinary transaction?
- Does the code actually behave as claimed?
- Is the impact caused by this code, not by a malicious validator, peer, or external dependency alone?
- Is the loss, divergence, halt, or resource exhaustion concrete, not hypothetical?
- Would an Anza triager accept the proof?
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
[Concrete in-scope impact, severity rationale, and bounty category]

## Likelihood Explanation
[Attacker capability, required conditions, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or fuzz/invariant/integration test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for agave.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production repo context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-user analogs in SVM loading, fee/rent accounting, compute budget, cost model, nonce/blockhash replay, or bank commit paths.
- Reject validator/peer/operator-role, mocked-only, theoretical-only, or no-impact analogs.
- Out of scope per SECURITY.md: dependencies and the sBPF interpreter, metrics, Geyser and `scheduler-bindings` external processes, Alpenglow/votor crates and plumbing, Loader V4 paths, maliciously crafted snapshots, bootstrap-phase-only issues fixable by config, and RPC DoS needing more than one call per `CLUSTER_SLOT_TIME_TARGET / 2`, multiple clients, or unfiltered getProgramAccounts without secondary indexes.

## Validate
- Map the bug class to the strongest reachable agave path.
- Prove root cause with exact file/function support.
- Accept only concrete value loss/creation, double settlement, cross-node divergence or halt, undeclared account mutation, or materially underpriced execution.

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
