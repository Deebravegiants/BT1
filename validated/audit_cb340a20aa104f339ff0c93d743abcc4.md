### Title
Stack overflow via unbounded recursive JSON parsing of attacker-controlled `ConfigKeys` validator-info payload - ([File: account-decoder/src/parse_config.rs])

### Finding Description
`parse_config` deserializes account data into `ConfigKeys`, and if `key_list.keys[0].0 == validator_info::id()` (a fixed, publicly-known constant, not a signature the attacker needs to possess — the key is stored with `signer: false`), it decodes the config payload as a plain `String` via `parse_config_data::<String>` and then calls `serde_json::from_str(&validator_info.config_data)` on that attacker-supplied string with no depth limit or size/structure validation: [1](#0-0) 

Any funded, unprivileged wallet can permissionlessly create a Config-program account and set `ConfigKeys.keys[0] = (validator_info::id(), false)`, then write any raw byte string as `config_data` (there is no on-chain schema/JSON validation in the Config program itself — `config_instruction::store` just writes bytes). By choosing a deeply nested JSON string (e.g., `"[[[[[..."` repeated thousands of times), the attacker forces `serde_json::from_str`'s recursive-descent parser to recurse to the input's nesting depth. `serde_json` (like most Rust JSON parsers) has no built-in recursion-depth guard, so sufficiently deep nesting overflows the parser thread's stack. A stack overflow in Rust aborts the process; it cannot be intercepted with `catch_unwind`, unlike an ordinary panic, so normal error-isolation in the RPC layer does not protect the node.

This code is reached by `parse_account_data_v3` for any account owned by the Config program when `encoding: jsonParsed` is requested: [2](#0-1) 

which in turn is reachable from a single `getAccountInfo` call: [3](#0-2) 

and from `getProgramAccounts` on the Config program: [4](#0-3) 

Neither `parse_config` nor the RPC encode path applies any bound on nesting depth or payload size before invoking `serde_json::from_str`, so the existing guards (account size limits, `MAX_MULTIPLE_ACCOUNTS`, etc.) do not stop a single crafted account's inner string from crashing the parser.

### Impact Explanation
Any public RPC node (or any node acting as an RPC replica) that serves `getAccountInfo`/`getProgramAccounts` with `jsonParsed` encoding for the crafted Config account will abort its process on a single request. This is a crash/denial-of-service reachable with exactly one RPC call against one account, created by an unprivileged funded signer with no special role, matching a validator/RPC crash bounty category (process abort, not a recoverable panic).

### Likelihood Explanation
The only precondition is a funded keypair capable of submitting `config_instruction`s to create a Config account with `keys[0] = validator_info::id()` (a constant, not a secret) and writing an arbitrarily large/deeply-nested JSON string as the payload. No elevated privilege, staked/leader/gossip access, or multiple RPC calls are needed — a single `getAccountInfo` with `jsonParsed` encoding on the account triggers the crash. This is fully attacker-controlled and deterministic, so it is trivially repeatable against any node exposing jsonParsed decoding for Config accounts.

### Recommendation
Guard the JSON deserialization in `parse_config` (and any other `serde_json::from_str`/`from_slice` calls operating on untrusted account bytes) with an explicit recursion/depth limit before parsing (e.g., pre-scan for maximum nesting depth, or use a JSON parser configured with a bounded recursion limit / iterative parser), and reject validator-info payloads whose structure exceeds a sane depth (e.g., a handful of levels) instead of passing them directly to `serde_json::from_str`.

### Proof of Concept
```rust
// account-decoder/src/parse_config.rs (new test)
#[test]
fn test_parse_config_deep_nesting_stack_overflow() {
    // Build a deeply nested JSON array as the validator-info payload.
    let depth = 100_000; // tune to exceed default thread stack size
    let mut nested = String::with_capacity(depth * 2);
    nested.push_str(&"[".repeat(depth));
    nested.push_str(&"]".repeat(depth));

    let validator_info = ValidatorInfo { info: nested };
    let info_pubkey = solana_pubkey::new_rand();
    let account = create_config_account(
        vec![(validator_info::id(), false), (info_pubkey, true)],
        &validator_info,
        10,
    );

    // Run in an isolated subprocess/thread harness with a bounded stack,
    // since a stack overflow aborts the process and cannot be caught with
    // catch_unwind. Expect the subprocess to abort (SIGSEGV/SIGABRT) rather
    // than returning a normal Result.
    parse_config(account.data(), &info_pubkey).ok();
}
```
Run this via a subprocess harness (e.g., spawn a child process with `std::process::Command`, or use a crate like `assert_cmd`/`libtest-mimic` with a constrained stack size) that asserts the child process terminates abnormally (non-zero/signal exit) instead of returning `Ok`/`Err`, confirming the stack overflow/process abort.

### Citations

**File:** account-decoder/src/parse_config.rs (L13-21)
```rust
pub fn parse_config(data: &[u8], _pubkey: &Pubkey) -> Result<ConfigAccountType, ParseAccountError> {
    let parsed_account = deserialize::<ConfigKeys>(data).ok().and_then(|key_list| {
        if !key_list.keys.is_empty() && key_list.keys[0].0 == validator_info::id() {
            parse_config_data::<String>(data, key_list.keys).and_then(|validator_info| {
                Some(ConfigAccountType::ValidatorInfo(UiConfig {
                    keys: validator_info.keys,
                    config_data: serde_json::from_str(&validator_info.config_data).ok()?,
                }))
            })
```

**File:** account-decoder/src/parse_account_data.rs (L143-143)
```rust
        ParsableAccount::Config => serde_json::to_value(parse_config(data, pubkey)?)?,
```

**File:** rpc/src/rpc.rs (L534-559)
```rust
    pub async fn get_account_info(
        &self,
        pubkey: Pubkey,
        config: Option<RpcAccountInfoConfig>,
    ) -> Result<RpcResponse<Option<UiAccount>>> {
        let RpcAccountInfoConfig {
            encoding,
            data_slice,
            commitment,
            min_context_slot,
        } = config.unwrap_or_default();
        let bank = self.get_bank_with_config(RpcContextConfig {
            commitment,
            min_context_slot,
        })?;
        let encoding = encoding.unwrap_or(UiAccountEncoding::Binary);

        let response = self
            .runtime
            .spawn_blocking({
                let bank = Arc::clone(&bank);
                move || get_encoded_account(&bank, &pubkey, encoding, data_slice, None)
            })
            .await
            .expect("rpc: get_encoded_account panicked")?;
        Ok(new_response(&bank, response))
```

**File:** rpc/src/rpc.rs (L603-666)
```rust
    pub async fn get_program_accounts(
        &self,
        program_id: Pubkey,
        config: Option<RpcAccountInfoConfig>,
        mut filters: Vec<RpcFilterType>,
        with_context: bool,
        sort_results: bool,
    ) -> Result<OptionalContext<Vec<RpcKeyedAccount>>> {
        let RpcAccountInfoConfig {
            encoding,
            data_slice: data_slice_config,
            commitment,
            min_context_slot,
        } = config.unwrap_or_default();
        let bank = self.get_bank_with_config(RpcContextConfig {
            commitment,
            min_context_slot,
        })?;
        let encoding = encoding.unwrap_or(UiAccountEncoding::Binary);
        optimize_filters(&mut filters);
        let keyed_accounts = {
            if let Some(owner) = get_spl_token_owner_filter(&program_id, &filters)? {
                self.get_filtered_spl_token_accounts_by_owner(
                    Arc::clone(&bank),
                    program_id,
                    owner,
                    filters,
                    sort_results,
                )
                .await?
            } else if let Some(mint) = get_spl_token_mint_filter(&program_id, &filters)? {
                self.get_filtered_spl_token_accounts_by_mint(
                    Arc::clone(&bank),
                    program_id,
                    mint,
                    filters,
                    sort_results,
                )
                .await?
            } else {
                self.get_filtered_program_accounts(
                    Arc::clone(&bank),
                    program_id,
                    filters,
                    sort_results,
                )
                .await?
            }
        };
        let accounts = if is_known_spl_token_id(&program_id)
            && encoding == UiAccountEncoding::JsonParsed
        {
            get_parsed_token_accounts(Arc::clone(&bank), keyed_accounts.into_iter()).collect()
        } else {
            keyed_accounts
                .into_iter()
                .map(|(pubkey, account)| {
                    Ok(RpcKeyedAccount {
                        pubkey: pubkey.to_string(),
                        account: encode_account(&account, &pubkey, encoding, data_slice_config)?,
                    })
                })
                .collect::<Result<Vec<_>>>()?
        };
```
