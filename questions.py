import json
import os

MAX_REPO = 25
SOURCE_REPO = 'aptos-labs/aptos-core'
REPO_NAME = 'aptos-core'
run_number = os.environ.get("GITHUB_RUN_NUMBER") or os.environ.get(
    "CI_PIPELINE_IID", "0"
)


def get_cyclic_index(run_number, max_index=100):
    """Convert run number to a cyclic index between 1 and max_index."""
    return (int(run_number) - 1) % max_index + 1


def load_repository_urls():
    """Load repository URLs from repositories.json."""
    repo_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "repositories.json"
    )
    if not os.path.exists(repo_file):
        return []

    try:
        with open(repo_file, "r", encoding="utf-8") as f:
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
    'api/src/accept_type.rs',
    'api/src/accounts.rs',
    'api/src/basic.rs',
    'api/src/bcs_payload.rs',
    'api/src/blocks.rs',
    'api/src/check_size.rs',
    'api/src/context.rs',
    'api/src/error_converter.rs',
    'api/src/events.rs',
    'api/src/headers_sanity_check.rs',
    'api/src/index.rs',
    'api/src/page.rs',
    'api/src/response.rs',
    'api/src/runtime.rs',
    'api/src/state.rs',
    'api/src/transactions.rs',
    'api/src/view_function.rs',
    'api/types/src/account.rs',
    'api/types/src/address.rs',
    'api/types/src/block.rs',
    'api/types/src/bytecode.rs',
    'api/types/src/convert.rs',
    'api/types/src/error.rs',
    'api/types/src/hash.rs',
    'api/types/src/headers.rs',
    'api/types/src/index.rs',
    'api/types/src/ledger_info.rs',
    'api/types/src/move_types.rs',
    'api/types/src/state.rs',
    'api/types/src/table.rs',
    'api/types/src/transaction.rs',
    'api/types/src/view.rs',
    'api/types/src/wrappers.rs',
    'aptos-move/aptos-aggregator/src/aggregator_v1_extension.rs',
    'aptos-move/aptos-aggregator/src/bounded_math.rs',
    'aptos-move/aptos-aggregator/src/delayed_change.rs',
    'aptos-move/aptos-aggregator/src/delayed_field_extension.rs',
    'aptos-move/aptos-aggregator/src/delta_change_set.rs',
    'aptos-move/aptos-aggregator/src/delta_math.rs',
    'aptos-move/aptos-aggregator/src/resolver.rs',
    'aptos-move/aptos-aggregator/src/types.rs',
    'aptos-move/aptos-gas-algebra/src/abstract_algebra.rs',
    'aptos-move/aptos-gas-algebra/src/algebra.rs',
    'aptos-move/aptos-gas-meter/src/algebra.rs',
    'aptos-move/aptos-gas-meter/src/meter.rs',
    'aptos-move/aptos-gas-meter/src/traits.rs',
    'aptos-move/aptos-gas-schedule/src/gas_schedule/aptos_framework.rs',
    'aptos-move/aptos-gas-schedule/src/gas_schedule/instr.rs',
    'aptos-move/aptos-gas-schedule/src/gas_schedule/macros.rs',
    'aptos-move/aptos-gas-schedule/src/gas_schedule/misc.rs',
    'aptos-move/aptos-gas-schedule/src/gas_schedule/move_stdlib.rs',
    'aptos-move/aptos-gas-schedule/src/gas_schedule/table.rs',
    'aptos-move/aptos-gas-schedule/src/gas_schedule/transaction.rs',
    'aptos-move/aptos-gas-schedule/src/traits.rs',
    'aptos-move/aptos-gas-schedule/src/ver.rs',
    'aptos-move/aptos-native-interface/src/builder.rs',
    'aptos-move/aptos-native-interface/src/context.rs',
    'aptos-move/aptos-native-interface/src/errors.rs',
    'aptos-move/aptos-native-interface/src/helpers.rs',
    'aptos-move/aptos-native-interface/src/native.rs',
    'aptos-move/aptos-native-interface/src/rayon_pool.rs',
    'aptos-move/aptos-native-interface/src/reexports.rs',
    'aptos-move/aptos-vm-environment/src/environment.rs',
    'aptos-move/aptos-vm-environment/src/gas.rs',
    'aptos-move/aptos-vm-environment/src/natives.rs',
    'aptos-move/aptos-vm-environment/src/prod_configs.rs',
    'aptos-move/aptos-vm-types/src/abstract_write_op.rs',
    'aptos-move/aptos-vm-types/src/change_set.rs',
    'aptos-move/aptos-vm-types/src/module_and_script_storage/code_storage.rs',
    'aptos-move/aptos-vm-types/src/module_and_script_storage/module_storage.rs',
    'aptos-move/aptos-vm-types/src/module_and_script_storage/read_recording.rs',
    'aptos-move/aptos-vm-types/src/module_and_script_storage/state_view_adapter.rs',
    'aptos-move/aptos-vm-types/src/module_write_set.rs',
    'aptos-move/aptos-vm-types/src/output.rs',
    'aptos-move/aptos-vm-types/src/resolver.rs',
    'aptos-move/aptos-vm-types/src/resource_group_adapter.rs',
    'aptos-move/aptos-vm-types/src/storage/change_set_configs.rs',
    'aptos-move/aptos-vm-types/src/storage/io_pricing.rs',
    'aptos-move/aptos-vm-types/src/storage/space_pricing.rs',
    'aptos-move/aptos-vm/src/aptos_vm.rs',
    'aptos-move/aptos-vm/src/block_executor/vm_wrapper.rs',
    'aptos-move/aptos-vm/src/data_cache.rs',
    'aptos-move/aptos-vm/src/errors.rs',
    'aptos-move/aptos-vm/src/gas.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/resolver.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/session/respawned_session.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/session/session_id.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/session/user_transaction_sessions/abort_hook.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/session/user_transaction_sessions/epilogue.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/session/user_transaction_sessions/prologue.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/session/user_transaction_sessions/session_change_sets.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/session/user_transaction_sessions/user.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/session/view_with_change_set.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/vm.rs',
    'aptos-move/aptos-vm/src/move_vm_ext/write_op_converter.rs',
    'aptos-move/aptos-vm/src/natives.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/aggr_overridden_state_view.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/coordinator_client.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/cross_shard_client.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/cross_shard_state_view.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/executor_client.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/global_executor.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/local_executor_shard.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/messages.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/remote_state_value.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/sharded_aggregator_service.rs',
    'aptos-move/aptos-vm/src/sharded_block_executor/sharded_executor_service.rs',
    'aptos-move/aptos-vm/src/system_module_names.rs',
    'aptos-move/aptos-vm/src/transaction_metadata.rs',
    'aptos-move/aptos-vm/src/transaction_validation.rs',
    'aptos-move/aptos-vm/src/transaction_validation_versioned.rs',
    'aptos-move/aptos-vm/src/validator_txns/chunky_dkg.rs',
    'aptos-move/aptos-vm/src/validator_txns/dkg.rs',
    'aptos-move/aptos-vm/src/validator_txns/jwk.rs',
    'aptos-move/aptos-vm/src/verifier/event_validation.rs',
    'aptos-move/aptos-vm/src/verifier/module_init.rs',
    'aptos-move/aptos-vm/src/verifier/native_validation.rs',
    'aptos-move/aptos-vm/src/verifier/resource_groups.rs',
    'aptos-move/aptos-vm/src/verifier/transaction_arg_validation.rs',
    'aptos-move/aptos-vm/src/verifier/view_function.rs',
    'aptos-move/block-executor/src/captured_reads.rs',
    'aptos-move/block-executor/src/code_cache.rs',
    'aptos-move/block-executor/src/code_cache_global.rs',
    'aptos-move/block-executor/src/code_cache_global_manager.rs',
    'aptos-move/block-executor/src/cold_validation.rs',
    'aptos-move/block-executor/src/errors.rs',
    'aptos-move/block-executor/src/executor.rs',
    'aptos-move/block-executor/src/executor_utilities.rs',
    'aptos-move/block-executor/src/explicit_sync_wrapper.rs',
    'aptos-move/block-executor/src/hot_state_op_accumulator.rs',
    'aptos-move/block-executor/src/limit_processor.rs',
    'aptos-move/block-executor/src/scheduler.rs',
    'aptos-move/block-executor/src/scheduler_status.rs',
    'aptos-move/block-executor/src/scheduler_v2.rs',
    'aptos-move/block-executor/src/scheduler_wrapper.rs',
    'aptos-move/block-executor/src/task.rs',
    'aptos-move/block-executor/src/txn_commit_hook.rs',
    'aptos-move/block-executor/src/txn_last_input_output.rs',
    'aptos-move/block-executor/src/txn_provider/blocking_txns_provider.rs',
    'aptos-move/block-executor/src/txn_provider/default.rs',
    'aptos-move/block-executor/src/types.rs',
    'aptos-move/block-executor/src/value_exchange.rs',
    'aptos-move/block-executor/src/view.rs',
    'aptos-move/block-executor/src/worker_pool.rs',
    'aptos-move/framework/aptos-framework/sources/account/account.move',
    'aptos-move/framework/aptos-framework/sources/account/auth_data.move',
    'aptos-move/framework/aptos-framework/sources/account/rate_limiter.move',
    'aptos-move/framework/aptos-framework/sources/aggregator/aggregator.move',
    'aptos-move/framework/aptos-framework/sources/aggregator/aggregator_factory.move',
    'aptos-move/framework/aptos-framework/sources/aggregator/optional_aggregator.move',
    'aptos-move/framework/aptos-framework/sources/aggregator_v2/aggregator_v2.move',
    'aptos-move/framework/aptos-framework/sources/aptos_account.move',
    'aptos-move/framework/aptos-framework/sources/aptos_coin.move',
    'aptos-move/framework/aptos-framework/sources/aptos_governance.move',
    'aptos-move/framework/aptos-framework/sources/block.move',
    'aptos-move/framework/aptos-framework/sources/chain_id.move',
    'aptos-move/framework/aptos-framework/sources/chain_status.move',
    'aptos-move/framework/aptos-framework/sources/chunky_dkg.move',
    'aptos-move/framework/aptos-framework/sources/code.move',
    'aptos-move/framework/aptos-framework/sources/coin.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_amount.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_asset.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_balance.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_range_proofs.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_key_rotation.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_registration.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_transfer.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_withdraw.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_fiat_shamir.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_homomorphism.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_proof.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_representation.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_representation_vec.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_statement.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_statement_builder.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_utils.move',
    'aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_witness.move',
    'aptos-move/framework/aptos-framework/sources/configs/chunky_dkg_config.move',
    'aptos-move/framework/aptos-framework/sources/configs/chunky_dkg_config_seqnum.move',
    'aptos-move/framework/aptos-framework/sources/configs/config_buffer.move',
    'aptos-move/framework/aptos-framework/sources/configs/consensus_config.move',
    'aptos-move/framework/aptos-framework/sources/configs/epoch_timeout_config.move',
    'aptos-move/framework/aptos-framework/sources/configs/execution_config.move',
    'aptos-move/framework/aptos-framework/sources/configs/gas_schedule.move',
    'aptos-move/framework/aptos-framework/sources/configs/jwk_consensus_config.move',
    'aptos-move/framework/aptos-framework/sources/configs/randomness_api_v0_config.move',
    'aptos-move/framework/aptos-framework/sources/configs/randomness_config.move',
    'aptos-move/framework/aptos-framework/sources/configs/randomness_config_seqnum.move',
    'aptos-move/framework/aptos-framework/sources/configs/staking_config.move',
    'aptos-move/framework/aptos-framework/sources/configs/version.move',
    'aptos-move/framework/aptos-framework/sources/create_signer.move',
    'aptos-move/framework/aptos-framework/sources/datastructures/big_ordered_map.move',
    'aptos-move/framework/aptos-framework/sources/datastructures/ordered_map.move',
    'aptos-move/framework/aptos-framework/sources/datastructures/storage_slot.move',
    'aptos-move/framework/aptos-framework/sources/datastructures/storage_slot_or_inline.move',
    'aptos-move/framework/aptos-framework/sources/decryption.move',
    'aptos-move/framework/aptos-framework/sources/delegation_pool.move',
    'aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move',
    'aptos-move/framework/aptos-framework/sources/dkg.move',
    'aptos-move/framework/aptos-framework/sources/event.move',
    'aptos-move/framework/aptos-framework/sources/function_info.move',
    'aptos-move/framework/aptos-framework/sources/fungible_asset.move',
    'aptos-move/framework/aptos-framework/sources/genesis.move',
    'aptos-move/framework/aptos-framework/sources/governance_proposal.move',
    'aptos-move/framework/aptos-framework/sources/guid.move',
    'aptos-move/framework/aptos-framework/sources/jwks.move',
    'aptos-move/framework/aptos-framework/sources/managed_coin.move',
    'aptos-move/framework/aptos-framework/sources/multisig_account.move',
    'aptos-move/framework/aptos-framework/sources/nonce_validation.move',
    'aptos-move/framework/aptos-framework/sources/object.move',
    'aptos-move/framework/aptos-framework/sources/object_code_deployment.move',
    'aptos-move/framework/aptos-framework/sources/primary_fungible_store.move',
    'aptos-move/framework/aptos-framework/sources/randomness.move',
    'aptos-move/framework/aptos-framework/sources/reconfiguration.move',
    'aptos-move/framework/aptos-framework/sources/reconfiguration_state.move',
    'aptos-move/framework/aptos-framework/sources/reconfiguration_with_dkg.move',
    'aptos-move/framework/aptos-framework/sources/resource_account.move',
    'aptos-move/framework/aptos-framework/sources/stake.move',
    'aptos-move/framework/aptos-framework/sources/staking_contract.move',
    'aptos-move/framework/aptos-framework/sources/staking_proxy.move',
    'aptos-move/framework/aptos-framework/sources/state_storage.move',
    'aptos-move/framework/aptos-framework/sources/storage_gas.move',
    'aptos-move/framework/aptos-framework/sources/system_addresses.move',
    'aptos-move/framework/aptos-framework/sources/timestamp.move',
    'aptos-move/framework/aptos-framework/sources/transaction_context.move',
    'aptos-move/framework/aptos-framework/sources/transaction_fee.move',
    'aptos-move/framework/aptos-framework/sources/transaction_limits.move',
    'aptos-move/framework/aptos-framework/sources/transaction_validation.move',
    'aptos-move/framework/aptos-framework/sources/util.move',
    'aptos-move/framework/aptos-framework/sources/validator_consensus_info.move',
    'aptos-move/framework/aptos-framework/sources/vesting.move',
    'aptos-move/framework/aptos-framework/sources/voting.move',
    'aptos-move/framework/aptos-stdlib/sources/any.move',
    'aptos-move/framework/aptos-stdlib/sources/bcs_stream.move',
    'aptos-move/framework/aptos-stdlib/sources/capability.move',
    'aptos-move/framework/aptos-stdlib/sources/comparator.move',
    'aptos-move/framework/aptos-stdlib/sources/copyable_any.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/bls12381.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/bls12381_algebra.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/bn254_algebra.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/crypto_algebra.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/ed25519.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/multi_ed25519.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/multi_key.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/ristretto255.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/ristretto255_bulletproofs.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/ristretto255_elgamal.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/ristretto255_pedersen.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/secp256k1.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/secp256r1.move',
    'aptos-move/framework/aptos-stdlib/sources/cryptography/single_key.move',
    'aptos-move/framework/aptos-stdlib/sources/data_structures/big_vector.move',
    'aptos-move/framework/aptos-stdlib/sources/data_structures/smart_table.move',
    'aptos-move/framework/aptos-stdlib/sources/data_structures/smart_vector.move',
    'aptos-move/framework/aptos-stdlib/sources/data_structures/storage_slots_allocator.move',
    'aptos-move/framework/aptos-stdlib/sources/debug.move',
    'aptos-move/framework/aptos-stdlib/sources/fixed_point64.move',
    'aptos-move/framework/aptos-stdlib/sources/from_bcs.move',
    'aptos-move/framework/aptos-stdlib/sources/hash.move',
    'aptos-move/framework/aptos-stdlib/sources/math128.move',
    'aptos-move/framework/aptos-stdlib/sources/math64.move',
    'aptos-move/framework/aptos-stdlib/sources/math_fixed.move',
    'aptos-move/framework/aptos-stdlib/sources/math_fixed64.move',
    'aptos-move/framework/aptos-stdlib/sources/pool_u64.move',
    'aptos-move/framework/aptos-stdlib/sources/pool_u64_unbound.move',
    'aptos-move/framework/aptos-stdlib/sources/simple_map.move',
    'aptos-move/framework/aptos-stdlib/sources/string_utils.move',
    'aptos-move/framework/aptos-stdlib/sources/table.move',
    'aptos-move/framework/aptos-stdlib/sources/table_with_length.move',
    'aptos-move/framework/aptos-stdlib/sources/type_info.move',
    'aptos-move/framework/aptos-token-objects/sources/aptos_token.move',
    'aptos-move/framework/aptos-token-objects/sources/collection.move',
    'aptos-move/framework/aptos-token-objects/sources/property_map.move',
    'aptos-move/framework/aptos-token-objects/sources/royalty.move',
    'aptos-move/framework/aptos-token-objects/sources/token.move',
    'aptos-move/framework/aptos-token/sources/property_map.move',
    'aptos-move/framework/aptos-token/sources/token.move',
    'aptos-move/framework/aptos-token/sources/token_coin_swap.move',
    'aptos-move/framework/aptos-token/sources/token_event_store.move',
    'aptos-move/framework/aptos-token/sources/token_transfers.move',
    'aptos-move/framework/move-stdlib/sources/acl.move',
    'aptos-move/framework/move-stdlib/sources/bcs.move',
    'aptos-move/framework/move-stdlib/sources/bit_vector.move',
    'aptos-move/framework/move-stdlib/sources/cmp.move',
    'aptos-move/framework/move-stdlib/sources/configs/features.move',
    'aptos-move/framework/move-stdlib/sources/error.move',
    'aptos-move/framework/move-stdlib/sources/fixed_point32.move',
    'aptos-move/framework/move-stdlib/sources/hash.move',
    'aptos-move/framework/move-stdlib/sources/mem.move',
    'aptos-move/framework/move-stdlib/sources/option.move',
    'aptos-move/framework/move-stdlib/sources/reflect.move',
    'aptos-move/framework/move-stdlib/sources/result.move',
    'aptos-move/framework/move-stdlib/sources/signer.move',
    'aptos-move/framework/move-stdlib/sources/string.move',
    'aptos-move/framework/move-stdlib/sources/vector.move',
    'aptos-move/framework/natives/src/account.rs',
    'aptos-move/framework/natives/src/aggregator_natives/aggregator.rs',
    'aptos-move/framework/natives/src/aggregator_natives/aggregator_factory.rs',
    'aptos-move/framework/natives/src/aggregator_natives/aggregator_v2.rs',
    'aptos-move/framework/natives/src/aggregator_natives/context.rs',
    'aptos-move/framework/natives/src/aggregator_natives/helpers_v1.rs',
    'aptos-move/framework/natives/src/aggregator_natives/helpers_v2.rs',
    'aptos-move/framework/natives/src/code.rs',
    'aptos-move/framework/natives/src/consensus_config.rs',
    'aptos-move/framework/natives/src/create_signer.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/add.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/div.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/double.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/inv.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/mul.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/neg.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/scalar_mul.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/sqr.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/arithmetics/sub.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/casting.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/constants.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/eq.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/hash_to_structure.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/new.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/pairing.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/rand.rs',
    'aptos-move/framework/natives/src/cryptography/algebra/serialization.rs',
    'aptos-move/framework/natives/src/cryptography/bls12381.rs',
    'aptos-move/framework/natives/src/cryptography/bulletproofs.rs',
    'aptos-move/framework/natives/src/cryptography/ed25519.rs',
    'aptos-move/framework/natives/src/cryptography/helpers.rs',
    'aptos-move/framework/natives/src/cryptography/multi_ed25519.rs',
    'aptos-move/framework/natives/src/cryptography/ristretto255.rs',
    'aptos-move/framework/natives/src/cryptography/ristretto255_point.rs',
    'aptos-move/framework/natives/src/cryptography/ristretto255_scalar.rs',
    'aptos-move/framework/natives/src/cryptography/secp256k1.rs',
    'aptos-move/framework/natives/src/debug.rs',
    'aptos-move/framework/natives/src/dispatchable_fungible_asset.rs',
    'aptos-move/framework/natives/src/event.rs',
    'aptos-move/framework/natives/src/function_info.rs',
    'aptos-move/framework/natives/src/hash.rs',
    'aptos-move/framework/natives/src/object.rs',
    'aptos-move/framework/natives/src/object_code_deployment.rs',
    'aptos-move/framework/natives/src/randomness.rs',
    'aptos-move/framework/natives/src/state_storage.rs',
    'aptos-move/framework/natives/src/storage_slot.rs',
    'aptos-move/framework/natives/src/string_utils.rs',
    'aptos-move/framework/natives/src/transaction_context.rs',
    'aptos-move/framework/natives/src/type_info.rs',
    'aptos-move/framework/natives/src/util.rs',
    'aptos-move/mvhashmap/src/registered_dependencies.rs',
    'aptos-move/mvhashmap/src/types.rs',
    'aptos-move/mvhashmap/src/unsync_map.rs',
    'aptos-move/mvhashmap/src/versioned_data.rs',
    'aptos-move/mvhashmap/src/versioned_delayed_fields.rs',
    'aptos-move/mvhashmap/src/versioned_group_data.rs',
    'aptos-move/vm-genesis/src/genesis_context.rs',
    'crates/aptos-crypto-derive/src/hasher.rs',
    'crates/aptos-crypto-derive/src/unions.rs',
    'crates/aptos-crypto/src/arkworks/differentiate.rs',
    'crates/aptos-crypto/src/arkworks/hashing.rs',
    'crates/aptos-crypto/src/arkworks/msm.rs',
    'crates/aptos-crypto/src/arkworks/random.rs',
    'crates/aptos-crypto/src/arkworks/scrape.rs',
    'crates/aptos-crypto/src/arkworks/serialization.rs',
    'crates/aptos-crypto/src/arkworks/shamir.rs',
    'crates/aptos-crypto/src/arkworks/srs.rs',
    'crates/aptos-crypto/src/arkworks/vanishing_poly.rs',
    'crates/aptos-crypto/src/arkworks/weighted_sum.rs',
    'crates/aptos-crypto/src/asymmetric_encryption/elgamal_curve25519_aes256_gcm.rs',
    'crates/aptos-crypto/src/bls12381/bls12381_keys.rs',
    'crates/aptos-crypto/src/bls12381/bls12381_pop.rs',
    'crates/aptos-crypto/src/bls12381/bls12381_sigs.rs',
    'crates/aptos-crypto/src/bls12381/bls12381_validatable.rs',
    'crates/aptos-crypto/src/blstrs/evaluation_domain.rs',
    'crates/aptos-crypto/src/blstrs/fft.rs',
    'crates/aptos-crypto/src/blstrs/lagrange.rs',
    'crates/aptos-crypto/src/blstrs/polynomials.rs',
    'crates/aptos-crypto/src/blstrs/random.rs',
    'crates/aptos-crypto/src/blstrs/scalar_secret_key.rs',
    'crates/aptos-crypto/src/blstrs/threshold_config.rs',
    'crates/aptos-crypto/src/compat.rs',
    'crates/aptos-crypto/src/constant_time/blstrs_scalar_mul.rs',
    'crates/aptos-crypto/src/constant_time/zkcrypto_scalar_mul.rs',
    'crates/aptos-crypto/src/ed25519/ed25519_keys.rs',
    'crates/aptos-crypto/src/ed25519/ed25519_sigs.rs',
    'crates/aptos-crypto/src/elgamal/curve25519.rs',
    'crates/aptos-crypto/src/encoding_type.rs',
    'crates/aptos-crypto/src/hash.rs',
    'crates/aptos-crypto/src/hkdf.rs',
    'crates/aptos-crypto/src/input_secret.rs',
    'crates/aptos-crypto/src/multi_ed25519.rs',
    'crates/aptos-crypto/src/noise.rs',
    'crates/aptos-crypto/src/player.rs',
    'crates/aptos-crypto/src/poseidon_bn254/alt_fr.rs',
    'crates/aptos-crypto/src/poseidon_bn254/constants.rs',
    'crates/aptos-crypto/src/secp256k1_ecdsa.rs',
    'crates/aptos-crypto/src/secp256r1_ecdsa/secp256r1_ecdsa_keys.rs',
    'crates/aptos-crypto/src/secp256r1_ecdsa/secp256r1_ecdsa_sigs.rs',
    'crates/aptos-crypto/src/slh_dsa_sha2_128s/slh_dsa_keys.rs',
    'crates/aptos-crypto/src/slh_dsa_sha2_128s/slh_dsa_sigs.rs',
    'crates/aptos-crypto/src/utils.rs',
    'crates/aptos-crypto/src/validatable.rs',
    'crates/aptos-crypto/src/weighted_config.rs',
    'crates/aptos-crypto/src/x25519.rs',
    'crates/aptos-dkg/src/dlog/bsgs.rs',
    'crates/aptos-dkg/src/dlog/table.rs',
    'crates/aptos-dkg/src/fiat_shamir.rs',
    'crates/aptos-dkg/src/pcs/shplonked.rs',
    'crates/aptos-dkg/src/pcs/shplonked_sigma.rs',
    'crates/aptos-dkg/src/pcs/traits.rs',
    'crates/aptos-dkg/src/pcs/univariate_hiding_kzg.rs',
    'crates/aptos-dkg/src/pcs/univariate_kzg.rs',
    'crates/aptos-dkg/src/pcs/zeromorph.rs',
    'crates/aptos-dkg/src/pvss/chunky/chunked_elgamal.rs',
    'crates/aptos-dkg/src/pvss/chunky/chunked_elgamal_pp.rs',
    'crates/aptos-dkg/src/pvss/chunky/chunked_scalar_mul.rs',
    'crates/aptos-dkg/src/pvss/chunky/chunks.rs',
    'crates/aptos-dkg/src/pvss/chunky/hkzg_chunked_elgamal.rs',
    'crates/aptos-dkg/src/pvss/chunky/hkzg_chunked_elgamal_commit.rs',
    'crates/aptos-dkg/src/pvss/chunky/input_secret.rs',
    'crates/aptos-dkg/src/pvss/chunky/keys.rs',
    'crates/aptos-dkg/src/pvss/chunky/public_parameters.rs',
    'crates/aptos-dkg/src/pvss/chunky/subtranscript.rs',
    'crates/aptos-dkg/src/pvss/chunky/verify_common.rs',
    'crates/aptos-dkg/src/pvss/chunky/weighted_transcript.rs',
    'crates/aptos-dkg/src/pvss/chunky/weighted_transcript_v2.rs',
    'crates/aptos-dkg/src/pvss/contribution.rs',
    'crates/aptos-dkg/src/pvss/das/enc.rs',
    'crates/aptos-dkg/src/pvss/das/input_secret.rs',
    'crates/aptos-dkg/src/pvss/das/public_parameters.rs',
    'crates/aptos-dkg/src/pvss/das/unweighted_protocol.rs',
    'crates/aptos-dkg/src/pvss/das/weighted_protocol.rs',
    'crates/aptos-dkg/src/pvss/dealt_pub_key.rs',
    'crates/aptos-dkg/src/pvss/dealt_pub_key_share.rs',
    'crates/aptos-dkg/src/pvss/dealt_secret_key.rs',
    'crates/aptos-dkg/src/pvss/dealt_secret_key_share.rs',
    'crates/aptos-dkg/src/pvss/encryption_dlog.rs',
    'crates/aptos-dkg/src/pvss/encryption_elgamal.rs',
    'crates/aptos-dkg/src/pvss/insecure_field/transcript.rs',
    'crates/aptos-dkg/src/pvss/schnorr.rs',
    'crates/aptos-dkg/src/pvss/signed/generic_signing.rs',
    'crates/aptos-dkg/src/pvss/traits/transcript.rs',
    'crates/aptos-dkg/src/pvss/weighted/generic_weighting.rs',
    'crates/aptos-dkg/src/range_proofs/dekart_univariate_v2.rs',
    'crates/aptos-dkg/src/range_proofs/scalars_to_bits.rs',
    'crates/aptos-dkg/src/range_proofs/traits.rs',
    'crates/aptos-dkg/src/sigma_protocol/homomorphism/fixed_base_msms.rs',
    'crates/aptos-dkg/src/sigma_protocol/homomorphism/tuple.rs',
    'crates/aptos-dkg/src/sigma_protocol/proof.rs',
    'crates/aptos-dkg/src/sigma_protocol/traits.rs',
    'crates/aptos-dkg/src/utils/parallel_multi_pairing.rs',
    'crates/aptos-dkg/src/utils/random.rs',
    'crates/aptos-dkg/src/weighted_vuf/traits.rs',
    'dkg/src/agg_trx_producer.rs',
    'dkg/src/chunky/agg_subtrx_producer.rs',
    'dkg/src/chunky/common.rs',
    'dkg/src/chunky/missing_transcript_fetcher.rs',
    'dkg/src/chunky/subtrx_cert_producer.rs',
    'dkg/src/chunky/types.rs',
    'dkg/src/epoch_manager.rs',
    'dkg/src/network.rs',
    'dkg/src/network_interface.rs',
    'dkg/src/types.rs',
    'execution/block-partitioner/src/main.rs',
    'execution/block-partitioner/src/pre_partition/connected_component/config.rs',
    'execution/block-partitioner/src/pre_partition/uniform_partitioner/config.rs',
    'execution/block-partitioner/src/sharded_block_partitioner/config.rs',
    'execution/block-partitioner/src/v2/build_edge.rs',
    'execution/block-partitioner/src/v2/config.rs',
    'execution/block-partitioner/src/v2/conflicting_txn_tracker.rs',
    'execution/block-partitioner/src/v2/init.rs',
    'execution/block-partitioner/src/v2/load_balance.rs',
    'execution/block-partitioner/src/v2/partition_to_matrix.rs',
    'execution/block-partitioner/src/v2/state.rs',
    'execution/block-partitioner/src/v2/types.rs',
    'execution/block-partitioner/src/v2/union_find.rs',
    'execution/executor-types/src/error.rs',
    'execution/executor-types/src/execution_output.rs',
    'execution/executor-types/src/ledger_update_output.rs',
    'execution/executor-types/src/planned.rs',
    'execution/executor-types/src/state_checkpoint_output.rs',
    'execution/executor-types/src/state_compute_result.rs',
    'execution/executor-types/src/transactions_with_output.rs',
    'execution/executor/src/chunk_executor/chunk_commit_queue.rs',
    'execution/executor/src/chunk_executor/chunk_result_verifier.rs',
    'execution/executor/src/chunk_executor/transaction_chunk.rs',
    'execution/executor/src/logging.rs',
    'execution/executor/src/types/executed_chunk.rs',
    'execution/executor/src/types/partial_state_compute_result.rs',
    'execution/executor/src/workflow/do_get_execution_output.rs',
    'execution/executor/src/workflow/do_ledger_update.rs',
    'execution/executor/src/workflow/do_state_checkpoint.rs',
    'mempool/src/core_mempool/index.rs',
    'mempool/src/core_mempool/mempool.rs',
    'mempool/src/core_mempool/transaction.rs',
    'mempool/src/core_mempool/transaction_store.rs',
    'mempool/src/logging.rs',
    'mempool/src/shared_mempool/coordinator.rs',
    'mempool/src/shared_mempool/network.rs',
    'mempool/src/shared_mempool/priority.rs',
    'mempool/src/shared_mempool/runtime.rs',
    'mempool/src/shared_mempool/tasks.rs',
    'mempool/src/shared_mempool/types.rs',
    'mempool/src/shared_mempool/use_case_history.rs',
    'storage/aptosdb/src/common.rs',
    'storage/aptosdb/src/db/aptosdb_internal.rs',
    'storage/aptosdb/src/db/aptosdb_native_position.rs',
    'storage/aptosdb/src/db/aptosdb_reader.rs',
    'storage/aptosdb/src/db/aptosdb_writer.rs',
    'storage/aptosdb/src/db_options.rs',
    'storage/aptosdb/src/fast_sync_storage_wrapper.rs',
    'storage/aptosdb/src/get_restore_handler.rs',
    'storage/aptosdb/src/ledger_db/event_db.rs',
    'storage/aptosdb/src/ledger_db/ledger_metadata_db.rs',
    'storage/aptosdb/src/ledger_db/persisted_auxiliary_info_db.rs',
    'storage/aptosdb/src/ledger_db/transaction_accumulator_db.rs',
    'storage/aptosdb/src/ledger_db/transaction_auxiliary_data_db.rs',
    'storage/aptosdb/src/ledger_db/transaction_db.rs',
    'storage/aptosdb/src/ledger_db/transaction_info_db.rs',
    'storage/aptosdb/src/ledger_db/write_set_db.rs',
    'storage/aptosdb/src/lru_node_cache.rs',
    'storage/aptosdb/src/native_state_committer.rs',
    'storage/aptosdb/src/position_buffered_state.rs',
    'storage/aptosdb/src/position_db.rs',
    'storage/aptosdb/src/position_merkle_batch_committer.rs',
    'storage/aptosdb/src/position_merkle_db.rs',
    'storage/aptosdb/src/position_pruner.rs',
    'storage/aptosdb/src/position_snapshot_committer.rs',
    'storage/aptosdb/src/position_state_store.rs',
    'storage/aptosdb/src/position_state_sync.rs',
    'storage/aptosdb/src/pruner/db_pruner.rs',
    'storage/aptosdb/src/pruner/db_sub_pruner.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/event_store_pruner.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/ledger_metadata_pruner.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/ledger_pruner_manager.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/persisted_auxiliary_info_pruner.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/transaction_accumulator_pruner.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/transaction_auxiliary_data_pruner.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/transaction_info_pruner.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/transaction_pruner.rs',
    'storage/aptosdb/src/pruner/ledger_pruner/write_set_pruner.rs',
    'storage/aptosdb/src/pruner/pruner_manager.rs',
    'storage/aptosdb/src/pruner/pruner_utils.rs',
    'storage/aptosdb/src/pruner/pruner_worker.rs',
    'storage/aptosdb/src/pruner/state_kv_pruner/generics.rs',
    'storage/aptosdb/src/pruner/state_kv_pruner/state_kv_metadata_pruner.rs',
    'storage/aptosdb/src/pruner/state_kv_pruner/state_kv_pruner_manager.rs',
    'storage/aptosdb/src/pruner/state_kv_pruner/state_kv_shard_pruner.rs',
    'storage/aptosdb/src/pruner/state_merkle_pruner/generics.rs',
    'storage/aptosdb/src/pruner/state_merkle_pruner/leaked_stale_node_cleaner.rs',
    'storage/aptosdb/src/pruner/state_merkle_pruner/state_merkle_metadata_pruner.rs',
    'storage/aptosdb/src/pruner/state_merkle_pruner/state_merkle_pruner_manager.rs',
    'storage/aptosdb/src/pruner/state_merkle_pruner/state_merkle_shard_pruner.rs',
    'storage/aptosdb/src/rocksdb_property_reporter.rs',
    'storage/aptosdb/src/sharded_jmt_merkle_db.rs',
    'storage/aptosdb/src/sharded_kv_db.rs',
    'storage/aptosdb/src/state_kv_db.rs',
    'storage/aptosdb/src/state_merkle_db.rs',
    'storage/aptosdb/src/state_store/buffered_state.rs',
    'storage/aptosdb/src/state_store/hot_state.rs',
    'storage/aptosdb/src/state_store/persisted_state.rs',
    'storage/aptosdb/src/state_store/state_merkle_batch_committer.rs',
    'storage/aptosdb/src/state_store/state_snapshot_committer.rs',
    'storage/aptosdb/src/state_value_chunk.rs',
    'storage/aptosdb/src/trading_native.rs',
    'storage/aptosdb/src/utils/iterators.rs',
    'storage/aptosdb/src/utils/truncation_helper.rs',
    'storage/aptosdb/src/versioned_node_cache.rs',
    'storage/schemadb/src/batch.rs',
    'storage/schemadb/src/iterator.rs',
    'storage/schemadb/src/schema.rs',
    'storage/scratchpad/src/sparse_merkle/dropper.rs',
    'storage/scratchpad/src/sparse_merkle/node.rs',
    'storage/scratchpad/src/sparse_merkle/updater.rs',
    'storage/scratchpad/src/sparse_merkle/utils.rs',
    'storage/storage-interface/src/block_info.rs',
    'storage/storage-interface/src/chunk_to_commit.rs',
    'storage/storage-interface/src/errors.rs',
    'storage/storage-interface/src/ledger_summary.rs',
    'storage/storage-interface/src/state_store/hot_state.rs',
    'storage/storage-interface/src/state_store/leaf_entry.rs',
    'storage/storage-interface/src/state_store/sharded_jmt_state.rs',
    'storage/storage-interface/src/state_store/state.rs',
    'storage/storage-interface/src/state_store/state_delta.rs',
    'storage/storage-interface/src/state_store/state_summary.rs',
    'storage/storage-interface/src/state_store/state_update_refs.rs',
    'storage/storage-interface/src/state_store/state_view/cached_state_view.rs',
    'storage/storage-interface/src/state_store/state_view/db_state_view.rs',
    'storage/storage-interface/src/state_store/state_view/hot_state_view.rs',
    'storage/storage-interface/src/state_store/state_with_summary.rs',
    'storage/storage-interface/src/state_store/versioned_state_value.rs',
    'third_party/move/move-binary-format/src/access.rs',
    'third_party/move/move-binary-format/src/binary_views.rs',
    'third_party/move/move-binary-format/src/builders.rs',
    'third_party/move/move-binary-format/src/check_bounds.rs',
    'third_party/move/move-binary-format/src/check_complexity.rs',
    'third_party/move/move-binary-format/src/compatibility.rs',
    'third_party/move/move-binary-format/src/constant.rs',
    'third_party/move/move-binary-format/src/control_flow_graph.rs',
    'third_party/move/move-binary-format/src/deserializer.rs',
    'third_party/move/move-binary-format/src/errors.rs',
    'third_party/move/move-binary-format/src/file_format.rs',
    'third_party/move/move-binary-format/src/file_format_common.rs',
    'third_party/move/move-binary-format/src/internals.rs',
    'third_party/move/move-binary-format/src/module_script_conversion.rs',
    'third_party/move/move-binary-format/src/serializer.rs',
    'third_party/move/move-binary-format/src/views.rs',
    'third_party/move/move-bytecode-verifier/src/absint.rs',
    'third_party/move/move-bytecode-verifier/src/acquires_list_verifier.rs',
    'third_party/move/move-bytecode-verifier/src/check_duplication.rs',
    'third_party/move/move-bytecode-verifier/src/code_unit_verifier.rs',
    'third_party/move/move-bytecode-verifier/src/constants.rs',
    'third_party/move/move-bytecode-verifier/src/control_flow.rs',
    'third_party/move/move-bytecode-verifier/src/control_flow_v5.rs',
    'third_party/move/move-bytecode-verifier/src/dependencies.rs',
    'third_party/move/move-bytecode-verifier/src/features.rs',
    'third_party/move/move-bytecode-verifier/src/friends.rs',
    'third_party/move/move-bytecode-verifier/src/instantiation_loops.rs',
    'third_party/move/move-bytecode-verifier/src/instruction_consistency.rs',
    'third_party/move/move-bytecode-verifier/src/limits.rs',
    'third_party/move/move-bytecode-verifier/src/locals_safety/abstract_state.rs',
    'third_party/move/move-bytecode-verifier/src/loop_summary.rs',
    'third_party/move/move-bytecode-verifier/src/meter.rs',
    'third_party/move/move-bytecode-verifier/src/reference_safety/abstract_state.rs',
    'third_party/move/move-bytecode-verifier/src/regression_tests/bounds_check.rs',
    'third_party/move/move-bytecode-verifier/src/regression_tests/reference_analysis.rs',
    'third_party/move/move-bytecode-verifier/src/regression_tests/struct_api.rs',
    'third_party/move/move-bytecode-verifier/src/script_signature.rs',
    'third_party/move/move-bytecode-verifier/src/signature_v2.rs',
    'third_party/move/move-bytecode-verifier/src/stack_usage_verifier.rs',
    'third_party/move/move-bytecode-verifier/src/struct_api_checker.rs',
    'third_party/move/move-bytecode-verifier/src/struct_defs.rs',
    'third_party/move/move-bytecode-verifier/src/type_safety.rs',
    'third_party/move/move-bytecode-verifier/src/verifier.rs',
    'third_party/move/move-core/types/src/abi.rs',
    'third_party/move/move-core/types/src/ability.rs',
    'third_party/move/move-core/types/src/account_address.rs',
    'third_party/move/move-core/types/src/diag_writer.rs',
    'third_party/move/move-core/types/src/effects.rs',
    'third_party/move/move-core/types/src/errmap.rs',
    'third_party/move/move-core/types/src/function.rs',
    'third_party/move/move-core/types/src/gas_algebra.rs',
    'third_party/move/move-core/types/src/identifier.rs',
    'third_party/move/move-core/types/src/int256.rs',
    'third_party/move/move-core/types/src/language_storage.rs',
    'third_party/move/move-core/types/src/metadata.rs',
    'third_party/move/move-core/types/src/move_resource.rs',
    'third_party/move/move-core/types/src/parser.rs',
    'third_party/move/move-core/types/src/safe_serialize.rs',
    'third_party/move/move-core/types/src/state.rs',
    'third_party/move/move-core/types/src/transaction_argument.rs',
    'third_party/move/move-core/types/src/value.rs',
    'third_party/move/move-core/types/src/vm_status.rs',
    'third_party/move/move-vm/runtime/src/config.rs',
    'third_party/move/move-vm/runtime/src/data_cache.rs',
    'third_party/move/move-vm/runtime/src/debug.rs',
    'third_party/move/move-vm/runtime/src/execution_tracing/recorders.rs',
    'third_party/move/move-vm/runtime/src/execution_tracing/trace.rs',
    'third_party/move/move-vm/runtime/src/frame.rs',
    'third_party/move/move-vm/runtime/src/frame_type_cache.rs',
    'third_party/move/move-vm/runtime/src/interpreter.rs',
    'third_party/move/move-vm/runtime/src/interpreter_caches.rs',
    'third_party/move/move-vm/runtime/src/loader/function.rs',
    'third_party/move/move-vm/runtime/src/loader/modules.rs',
    'third_party/move/move-vm/runtime/src/loader/script.rs',
    'third_party/move/move-vm/runtime/src/loader/single_signature_loader.rs',
    'third_party/move/move-vm/runtime/src/loader/type_loader.rs',
    'third_party/move/move-vm/runtime/src/logging.rs',
    'third_party/move/move-vm/runtime/src/module_traversal.rs',
    'third_party/move/move-vm/runtime/src/move_vm.rs',
    'third_party/move/move-vm/runtime/src/native_extensions.rs',
    'third_party/move/move-vm/runtime/src/native_functions.rs',
    'third_party/move/move-vm/runtime/src/native_models_for_runtime_ref_checks.rs',
    'third_party/move/move-vm/runtime/src/reentrancy_checker.rs',
    'third_party/move/move-vm/runtime/src/runtime_ref_checks.rs',
    'third_party/move/move-vm/runtime/src/runtime_type_checks.rs',
    'third_party/move/move-vm/runtime/src/runtime_type_checks_async.rs',
    'third_party/move/move-vm/runtime/src/source_locator.rs',
    'third_party/move/move-vm/runtime/src/storage/code_storage.rs',
    'third_party/move/move-vm/runtime/src/storage/dependencies_gas_charging.rs',
    'third_party/move/move-vm/runtime/src/storage/environment.rs',
    'third_party/move/move-vm/runtime/src/storage/implementations/unsync_code_storage.rs',
    'third_party/move/move-vm/runtime/src/storage/implementations/unsync_module_storage.rs',
    'third_party/move/move-vm/runtime/src/storage/layout_cache.rs',
    'third_party/move/move-vm/runtime/src/storage/loader/eager.rs',
    'third_party/move/move-vm/runtime/src/storage/loader/lazy.rs',
    'third_party/move/move-vm/runtime/src/storage/loader/traits.rs',
    'third_party/move/move-vm/runtime/src/storage/module_storage.rs',
    'third_party/move/move-vm/runtime/src/storage/publishing.rs',
    'third_party/move/move-vm/runtime/src/storage/ty_depth_checker.rs',
    'third_party/move/move-vm/runtime/src/storage/ty_layout_converter.rs',
    'third_party/move/move-vm/runtime/src/storage/ty_tag_converter.rs',
    'third_party/move/move-vm/runtime/src/storage/verified_module_cache.rs',
    'third_party/move/move-vm/runtime/src/tracing.rs',
    'third_party/move/move-vm/types/src/code/cache/module_cache.rs',
    'third_party/move/move-vm/types/src/code/cache/script_cache.rs',
    'third_party/move/move-vm/types/src/code/cache/test_types.rs',
    'third_party/move/move-vm/types/src/code/cache/types.rs',
    'third_party/move/move-vm/types/src/code/errors.rs',
    'third_party/move/move-vm/types/src/code/storage.rs',
    'third_party/move/move-vm/types/src/delayed_values/delayed_field_id.rs',
    'third_party/move/move-vm/types/src/delayed_values/derived_string_snapshot.rs',
    'third_party/move/move-vm/types/src/delayed_values/error.rs',
    'third_party/move/move-vm/types/src/gas.rs',
    'third_party/move/move-vm/types/src/instr.rs',
    'third_party/move/move-vm/types/src/interner.rs',
    'third_party/move/move-vm/types/src/limits.rs',
    'third_party/move/move-vm/types/src/loaded_data/runtime_types.rs',
    'third_party/move/move-vm/types/src/loaded_data/struct_name_indexing.rs',
    'third_party/move/move-vm/types/src/module_id_interner.rs',
    'third_party/move/move-vm/types/src/natives/function.rs',
    'third_party/move/move-vm/types/src/resolver.rs',
    'third_party/move/move-vm/types/src/ty_interner.rs',
    'third_party/move/move-vm/types/src/value_serde.rs',
    'third_party/move/move-vm/types/src/value_traversal.rs',
    'third_party/move/move-vm/types/src/values/function_values_impl.rs',
    'third_party/move/move-vm/types/src/values/values_impl.rs',
    'third_party/move/move-vm/types/src/views.rs',
    'types/src/access_path.rs',
    'types/src/account_address.rs',
    'types/src/account_config/constants/account.rs',
    'types/src/account_config/constants/addresses.rs',
    'types/src/account_config/events/burn.rs',
    'types/src/account_config/events/burn_event.rs',
    'types/src/account_config/events/burn_token.rs',
    'types/src/account_config/events/burn_token_event.rs',
    'types/src/account_config/events/cancel_offer.rs',
    'types/src/account_config/events/claim.rs',
    'types/src/account_config/events/coin_deposit.rs',
    'types/src/account_config/events/coin_register.rs',
    'types/src/account_config/events/coin_register_event.rs',
    'types/src/account_config/events/coin_withdraw.rs',
    'types/src/account_config/events/collection_description_mutate.rs',
    'types/src/account_config/events/collection_description_mutate_event.rs',
    'types/src/account_config/events/collection_maximum_mutate.rs',
    'types/src/account_config/events/collection_maximum_mutate_event.rs',
    'types/src/account_config/events/collection_mutation.rs',
    'types/src/account_config/events/collection_mutation_event.rs',
    'types/src/account_config/events/collection_uri_mutate.rs',
    'types/src/account_config/events/collection_uri_mutate_event.rs',
    'types/src/account_config/events/create_collection.rs',
    'types/src/account_config/events/create_collection_event.rs',
    'types/src/account_config/events/create_token_data_event.rs',
    'types/src/account_config/events/default_property_mutate.rs',
    'types/src/account_config/events/default_property_mutate_event.rs',
    'types/src/account_config/events/deposit_event.rs',
    'types/src/account_config/events/description_mutate.rs',
    'types/src/account_config/events/description_mutate_event.rs',
    'types/src/account_config/events/fungible_asset.rs',
    'types/src/account_config/events/key_rotation.rs',
    'types/src/account_config/events/key_rotation_event.rs',
    'types/src/account_config/events/maximum_mutate.rs',
    'types/src/account_config/events/maximum_mutate_event.rs',
    'types/src/account_config/events/mint.rs',
    'types/src/account_config/events/mint_event.rs',
    'types/src/account_config/events/mint_token.rs',
    'types/src/account_config/events/mint_token_event.rs',
    'types/src/account_config/events/mutate_property_map.rs',
    'types/src/account_config/events/mutate_token_property_map_event.rs',
    'types/src/account_config/events/new_block.rs',
    'types/src/account_config/events/new_epoch.rs',
    'types/src/account_config/events/offer.rs',
    'types/src/account_config/events/opt_in_transfer.rs',
    'types/src/account_config/events/opt_in_transfer_event.rs',
    'types/src/account_config/events/randomness_event.rs',
    'types/src/account_config/events/royalty_mutate.rs',
    'types/src/account_config/events/royalty_mutate_event.rs',
    'types/src/account_config/events/token_cancel_offer_event.rs',
    'types/src/account_config/events/token_claim_event.rs',
    'types/src/account_config/events/token_data_creation.rs',
    'types/src/account_config/events/token_deposit.rs',
    'types/src/account_config/events/token_deposit_event.rs',
    'types/src/account_config/events/token_mutation.rs',
    'types/src/account_config/events/token_mutation_event.rs',
    'types/src/account_config/events/token_offer_event.rs',
    'types/src/account_config/events/token_withdraw.rs',
    'types/src/account_config/events/token_withdraw_event.rs',
    'types/src/account_config/events/transfer.rs',
    'types/src/account_config/events/transfer_event.rs',
    'types/src/account_config/events/uri_mutation.rs',
    'types/src/account_config/events/uri_mutation_event.rs',
    'types/src/account_config/events/withdraw_event.rs',
    'types/src/account_config/resources/aggregator.rs',
    'types/src/account_config/resources/any.rs',
    'types/src/account_config/resources/chain_id.rs',
    'types/src/account_config/resources/challenge.rs',
    'types/src/account_config/resources/coin_info.rs',
    'types/src/account_config/resources/coin_store.rs',
    'types/src/account_config/resources/collection.rs',
    'types/src/account_config/resources/collections.rs',
    'types/src/account_config/resources/core_account.rs',
    'types/src/account_config/resources/fixed_supply.rs',
    'types/src/account_config/resources/fungible_asset_metadata.rs',
    'types/src/account_config/resources/fungible_store.rs',
    'types/src/account_config/resources/object.rs',
    'types/src/account_config/resources/pending_claims.rs',
    'types/src/account_config/resources/token.rs',
    'types/src/account_config/resources/token_event_store_v1.rs',
    'types/src/account_config/resources/token_store.rs',
    'types/src/account_config/resources/type_info.rs',
    'types/src/account_config/resources/unlimited_supply.rs',
    'types/src/aggregate_signature.rs',
    'types/src/block_executor/config.rs',
    'types/src/block_executor/output.rs',
    'types/src/block_executor/partitioner.rs',
    'types/src/block_executor/transaction_slice_metadata.rs',
    'types/src/block_executor/value.rs',
    'types/src/block_info.rs',
    'types/src/block_metadata.rs',
    'types/src/block_metadata_ext.rs',
    'types/src/bytes.rs',
    'types/src/chain_id.rs',
    'types/src/contract_event.rs',
    'types/src/decryption.rs',
    'types/src/delayed_fields.rs',
    'types/src/dkg/chunky_dkg.rs',
    'types/src/dkg/randomness_dkg.rs',
    'types/src/epoch_change.rs',
    'types/src/epoch_state.rs',
    'types/src/error.rs',
    'types/src/event.rs',
    'types/src/executable.rs',
    'types/src/fee_statement.rs',
    'types/src/function_info.rs',
    'types/src/governance.rs',
    'types/src/lazy_bls.rs',
    'types/src/ledger_info.rs',
    'types/src/mempool_status.rs',
    'types/src/move_any.rs',
    'types/src/move_fixed_point.rs',
    'types/src/move_utils/as_move_value.rs',
    'types/src/move_utils/move_event_v1.rs',
    'types/src/move_utils/move_event_v2.rs',
    'types/src/object_address.rs',
    'types/src/on_chain_config/approved_execution_hashes.rs',
    'types/src/on_chain_config/aptos_features.rs',
    'types/src/on_chain_config/aptos_version.rs',
    'types/src/on_chain_config/chain_id.rs',
    'types/src/on_chain_config/chunky_dkg_config.rs',
    'types/src/on_chain_config/commit_history.rs',
    'types/src/on_chain_config/consensus_config.rs',
    'types/src/on_chain_config/epoch_timeout_config.rs',
    'types/src/on_chain_config/execution_config.rs',
    'types/src/on_chain_config/gas_schedule.rs',
    'types/src/on_chain_config/jwk_consensus_config.rs',
    'types/src/on_chain_config/randomness_api_v0_config.rs',
    'types/src/on_chain_config/randomness_config.rs',
    'types/src/on_chain_config/timed_features.rs',
    'types/src/on_chain_config/timestamp.rs',
    'types/src/on_chain_config/transaction_fee.rs',
    'types/src/on_chain_config/validator_set.rs',
    'types/src/proof/definition.rs',
    'types/src/randomness.rs',
    'types/src/secret_sharing.rs',
    'types/src/serde_helper/bcs_utils.rs',
    'types/src/serde_helper/vec_bytes.rs',
    'types/src/stake_pool.rs',
    'types/src/staking_contract.rs',
    'types/src/state_proof.rs',
    'types/src/state_store/errors.rs',
    'types/src/state_store/hot_state.rs',
    'types/src/state_store/native_position.rs',
    'types/src/state_store/state_key/inner.rs',
    'types/src/state_store/state_key/prefix.rs',
    'types/src/state_store/state_key/registry.rs',
    'types/src/state_store/state_slot.rs',
    'types/src/state_store/state_storage_usage.rs',
    'types/src/state_store/state_value.rs',
    'types/src/state_store/table.rs',
    'types/src/timestamp.rs',
    'types/src/transaction/analyzed_transaction.rs',
    'types/src/transaction/authenticator.rs',
    'types/src/transaction/block_epilogue.rs',
    'types/src/transaction/block_output.rs',
    'types/src/transaction/change_set.rs',
    'types/src/transaction/encrypted_payload.rs',
    'types/src/transaction/module.rs',
    'types/src/transaction/multisig.rs',
    'types/src/transaction/script.rs',
    'types/src/transaction/signature_verified_transaction.rs',
    'types/src/transaction/use_case.rs',
    'types/src/transaction/user_transaction_context.rs',
    'types/src/transaction/webauthn.rs',
    'types/src/trusted_state.rs',
    'types/src/utility_coin.rs',
    'types/src/validator_config.rs',
    'types/src/validator_info.rs',
    'types/src/validator_performances.rs',
    'types/src/validator_signer.rs',
    'types/src/validator_txn.rs',
    'types/src/validator_verifier.rs',
    'types/src/vesting.rs',
    'types/src/vm/code.rs',
    'types/src/vm/module_metadata.rs',
    'types/src/vm/modules.rs',
    'types/src/vm_status.rs',
    'types/src/waypoint.rs',
    'types/src/write_set.rs',
    'vm-validator/src/vm_validator.rs',
]

target_scopes = [
    'Critical. An unprivileged attacker can transfer, mint, burn, freeze, or reassign APT, fungible assets, or token objects through object, fungible-asset, or account state transitions.',
    'Critical. An unprivileged attacker can take over or permanently lock object-held, multisig-controlled, or resource-account-held value through ownership or capability confusion.',
    'High. An unprivileged attacker can change asset control state such as metadata ownership, freeze authority, dispatch hooks, or code-object ownership without the required authority.',
    'High. Unprivileged input can break custody accounting across deposit, withdraw, transfer, split, merge, or burn flows and credit the wrong holder or debit the wrong holder.',
    'Critical. An unprivileged attacker can seize code-object or resource-account control in a way that later enables theft, freeze, or malicious upgrade of live assets.',
]

APTOS_ALLOWED_IMPACT_SCOPE = """## Custody Impact Gate
Accept only custody-grade, mainnet-relevant impacts tied to asset and ownership control."""

APTOS_AUDIT_PIVOTS = """## Custody Pivots
- Object creation, transfer, burn, extensibility, and ownership refs must preserve the intended controller.
- Fungible asset metadata, primary and secondary stores, dispatchable hooks, and freeze state must preserve supply and holder identity.
- Multisig-owned assets, resource accounts, and code objects must not leak upgrade, freeze, or transfer authority to unprivileged callers.
- Custody invariants should hold across deposit, withdraw, transfer, split, merge, burn, and store-creation paths."""


def question_generator(target_file: str) -> str:
    """
    Generate security questions for one Aptos Core target.
    """

    prompt = f"""
    Build 18 to 24 Aptos custody questions for this exact file:
    {target_file}

    Focus:
    Stay on live mainnet custody surfaces: objects, fungible assets, token objects, resource accounts, multisig-held assets, and code objects that control value.

    {APTOS_ALLOWED_IMPACT_SCOPE}

    {APTOS_AUDIT_PIVOTS}

    Rules:
    * `File Name:` must be this file. `Scope:` must be exactly one `target_scopes` item.
    * Use repo context as-is. Do not ask for more files or extra explanation.
    * The attacker is strictly unprivileged. Do not assume validator, peer, node, admin, governance, signer, leaked key, database, or infra control.
    * Do not assume the attacker already has owner, signer, publisher, multisig, capability, resource-account, or code-object permission.
    * Discard peer-driven, generic DoS, Consensus Observer-only, `consensus/src/dag`, `experimental`, `keyless/pepper`, AIP-103, and AIP-104 ideas.
    * Discard questions based only on unbounded input size, storage growth, queue growth, or spam volume without a concrete in-scope high or critical custody break.
    * Ignore tests, mocks, fixtures, benches, examples, docs, readmes, generated or build files, `.toml`, event-only mismatches, rounding dust, style, and dependency-only behavior.
    * Write 18 to 24 non-overlapping, high-signal questions.
    * Name the exact corrupted value: balance, owner, metadata owner, freeze status, dispatch hook, multisig control, resource-account control, code object owner, or API response object.
    * Every question must be testable with a Rust or Move unit, integration, property, or fuzz-style test.

    Each question must include target symbol, attacker input, required state, call path, broken invariant, corrupted value, scoped impact, and proof idea.

    Return Python only.
    
    Note u must follow the qwuestion format 

    questions = [
    "[File: {target_file}]  Can attacker-controlled INPUT under REQUIRED_STATE cross a custody boundary in CALL_PATH and break MAINNET_CUSTODY_INVARIANT, corrupting EXACT_VALUE with scoped impact SCOPE_IMPACT? Proof idea: write a focused repo test that drives ENTRYPOINT and asserts EXPECTED_OWNERSHIP_OR_BALANCE_PROPERTY.",
    ]
    """
    return prompt


def audit_format(question: str) -> str:
    """
    Generate a focused Aptos exploit-question validation prompt.
    """
    return f"""# APTOS CUSTODY REVIEW

## Submitted Question
{question}

## Review Bounds
- Review Aptos production custody logic only.
- The path must start from unprivileged transaction, package, view, authenticator, API, bytecode, or proof input.
- Ignore malicious peer or node behavior, generic network DoS, local tooling, and excluded scope areas.

## Decision Standard
Call it valid only if unprivileged input crosses a real custody boundary and changes who can own, move, mint, burn, freeze, upgrade, or recover value. Reject anything that needs pre-existing permissions or only produces cosmetic or event-level mismatch.

## Required Impacts
{APTOS_ALLOWED_IMPACT_SCOPE}

{APTOS_AUDIT_PIVOTS}

## Review Path
1. Trace the unprivileged entrypoint into the exact custody surface.
2. Map the controller, holder, and capability state before and after the path.
3. Name the wrong balance, owner, authority, or recovery right.
4. Reject if authority checks or ownership refs already close the path.

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
    Generate a cross-project analog scan prompt for Aptos issues.
    """
    prompt = f"""# CUSTODY ANALOG SCAN

## External Report
{report}

## Task
Use the external report only as a bug-class seed. Search for a new Aptos-native custody analog in object, fungible-asset, multisig, resource-account, or code-object flows.

## Required Impacts
{APTOS_ALLOWED_IMPACT_SCOPE}

{APTOS_AUDIT_PIVOTS}

Internally generate 2 to 4 candidate custody paths, keep the strongest one, and report it only if local code proves its own unprivileged root cause, broken custody invariant, exact corrupted value, and high or critical impact. Do not just restate the external bug.

## Search Steps
1. Reduce the external bug to one custody invariant.
2. Generate 2 to 4 local candidate paths in scoped code.
3. Keep only the strongest candidate with exact file and function support.
4. Trace input -> authority break -> corrupted balance, owner, or control field -> impact.
5. If the local path does not independently hold, return `#NoVulnerability found for this question.`

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
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict Aptos validation prompt for security claims.
    """
    prompt = f"""# CUSTODY CLAIM VALIDATION

## Security Claim
{report}

## Rules
- Validate only the submitted claim against Aptos production custody code in this repository.
- Do not widen the claim, change target scope, or raise severity without evidence.
- A valid issue must come from an unprivileged external attacker using transaction, package, view, authenticator, API, or proof inputs exposed by scoped code.
- Reject malicious peer or node behavior, generic network DoS, Consensus Observer-only impact, `consensus/src/dag`, `experimental`, `keyless/pepper`, AIP-103 Permissioned Signer, and AIP-104 Account Abstraction.
- Reject leaked keys, privileged governance or validator powers, off-repo infra control, pre-existing permissions, config-only mistakes, and non-production artifacts.
- The final impact must match one `target_scopes` item or the custody gate below and must name the exact corrupted value.

## Required Impacts
{APTOS_ALLOWED_IMPACT_SCOPE}

{APTOS_AUDIT_PIVOTS}

## Required Checks
1. Exact file and function references in scoped code.
2. A clear custody invariant tied to asset ownership, control, or recovery.
3. A reachable path from attacker input to bad balance, owner, or authority state.
4. Existing guards reviewed and shown insufficient.
5. Exact wrong value named: balance, owner, metadata owner, freeze status, dispatch hook, multisig control, resource-account control, code object owner, or API object.
6. A reproducible proof path via Rust or Move unit, integration, property, or fuzz-style testing.

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
[Concrete allowed repository impact and severity rationale]

## Likelihood Explanation
[Attacker capability, required conditions, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt
