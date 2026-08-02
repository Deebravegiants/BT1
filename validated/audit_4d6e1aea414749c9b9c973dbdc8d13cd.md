[1](#0-0)

### Citations

**File:** api/src/context.rs (L1-50)
```rust
// Copyright (c) Aptos Foundation
// Licensed pursuant to the Innovation-Enabling Source Code License, available at https://github.com/aptos-labs/aptos-core/blob/main/LICENSE

use crate::{
    accept_type::AcceptType,
    metrics,
    response::{
        bcs_api_disabled, block_not_found_by_height, block_not_found_by_version,
        block_pruned_by_height, json_api_disabled, version_not_found, version_pruned,
        ForbiddenError, InternalError, NotFoundError, ServiceUnavailableError, StdApiError,
    },
};
use anyhow::{anyhow, ensure, format_err, Context as AnyhowContext, Result};
use aptos_api_types::{
    transaction::ReplayProtector, AptosErrorCode, AsConverter, BcsBlock, GasEstimation, LedgerInfo,
    ResourceGroup, TransactionOnChainData, TransactionSummary,
};
use aptos_config::config::{GasEstimationConfig, NodeConfig, RoleType};
use aptos_crypto::HashValue;
use aptos_gas_schedule::{AptosGasParameters, FromOnChainGasSchedule};
use aptos_logger::{error, info, Schema};
use aptos_mempool::{MempoolClientRequest, MempoolClientSender, SubmissionStatus};
use aptos_storage_interface::{
    state_store::state_view::db_state_view::{
        DbStateView, DbStateViewAtVersion, LatestDbStateCheckpointView,
    },
    AptosDbError, DbReader, Order,
};
use aptos_types::{
    access_path::{AccessPath, Path},
    account_address::AccountAddress,
    account_config::{AccountResource, NewBlockEvent},
    chain_id::ChainId,
    contract_event::{ContractEvent, ContractEventV1, EventWithVersion},
    event::EventKey,
    indexer::indexer_db_reader::IndexerReader,
    ledger_info::LedgerInfoWithSignatures,
    on_chain_config::{
        FeatureFlag, Features, GasSchedule, GasScheduleV2, OnChainConfig, OnChainExecutionConfig,
    },
    state_store::{
        state_key::{inner::StateKeyInner, prefix::StateKeyPrefix, StateKey},
        TStateView,
    },
    transaction::{
        block_epilogue::BlockEndInfo,
        use_case::{UseCaseAwareTransaction, UseCaseKey},
        IndexedTransactionSummary, SignedTransaction, Transaction, TransactionWithProof, Version,
    },
};
```
