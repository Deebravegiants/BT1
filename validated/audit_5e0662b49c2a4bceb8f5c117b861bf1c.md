[1](#0-0)

### Citations

**File:** third_party/move/move-vm/types/src/loaded_data/runtime_types.rs (L1-38)
```rust
// Parts of the file are Copyright (c) The Diem Core Contributors
// Parts of the file are Copyright (c) The Move Contributors
// Parts of the file are Copyright (c) Aptos Foundation
// All Aptos Foundation code and content is licensed pursuant to the Innovation-Enabling Source Code License, available at https://github.com/aptos-labs/aptos-core/blob/main/LICENSE

#![allow(clippy::non_canonical_partial_ord_impl)]

use crate::{
    loaded_data::struct_name_indexing::StructNameIndex,
    module_id_interner::{InternedModuleId, InternedModuleIdPool},
};
use derivative::Derivative;
use itertools::Itertools;
use move_binary_format::{
    errors::{PartialVMError, PartialVMResult},
    file_format::{
        SignatureToken, StructHandle, StructTypeParameter, TypeParameterIndex, VariantIndex,
    },
};
use move_core_types::{
    ability::{Ability, AbilitySet},
    function::ClosureMask,
    identifier::Identifier,
    language_storage::{FunctionParamOrReturnTag, FunctionTag, ModuleId, StructTag, TypeTag},
    vm_status::{sub_status::unknown_invariant_violation::EPARANOID_FAILURE, StatusCode},
};
use serde::Serialize;
use smallbitvec::SmallBitVec;
use smallvec::{smallvec, SmallVec};
use std::{
    cell::RefCell,
    cmp::max,
    collections::{btree_map, BTreeMap},
    fmt,
    fmt::Debug,
    sync::Arc,
};
use triomphe::Arc as TriompheArc;
```
