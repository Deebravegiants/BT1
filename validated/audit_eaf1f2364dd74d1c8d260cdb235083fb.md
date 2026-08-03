No vulnerability found for this question.

**Rationale:**

Both `set_for_next_epoch` and `set_allow_max_gas_flag_for_next_epoch` in `randomness_api_v0_config.move` require `system_addresses::assert_aptos_framework(framework)` before writing to the `config_buffer`, and `on_new_epoch` similarly asserts the caller is the framework signer [1](#0-0) . There is no unprivileged entrypoint that can independently stage or trigger application of either `RequiredGasDeposit` or `AllowCustomMaxGasFlag` — both configs can only be buffered by aptos governance (via `aptos_governance`), and `on_new_epoch` only runs during framework-driven reconfiguration [2](#0-1) . This fails the review bound requiring the path to start from unprivileged input.

Separately, even granting governance access, the two configs are independently-settable by design — there is no documented invariant that they must change atomically together, and `RandomnessConfig::fetch` in the VM simply reads whatever the current committed values are at the time of a transaction, defaulting safely to `false`/`None` if missing [3](#0-2) . A stale `RequiredGasDeposit.gas_amount` paired with a freshly-updated `AllowCustomMaxGasFlag.value` at worst changes which gas amount is used as the anti-bias deposit for `#[randomness()]` entry functions — this affects a bias-resistance/gas-metering parameter, not custody of assets (ownership, transfer, mint/burn, freeze, or upgrade authority over any object, fungible asset store, or resource account). It does not meet the Custody Impact Gate requiring asset/ownership-control impact.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/configs/randomness_api_v0_config.move (L26-56)
```text
    public fun set_for_next_epoch(framework: &signer, gas_amount: Option<u64>) {
        system_addresses::assert_aptos_framework(framework);
        config_buffer::upsert(RequiredGasDeposit { gas_amount });
    }

    /// This can be called by on-chain governance to update `AllowCustomMaxGasFlag` for the next epoch.
    public fun set_allow_max_gas_flag_for_next_epoch(framework: &signer, value: bool) {
        system_addresses::assert_aptos_framework(framework);
        config_buffer::upsert(AllowCustomMaxGasFlag { value } );
    }

    /// Only used in reconfigurations to apply the pending `RequiredGasDeposit`, if there is any.
    public fun on_new_epoch(framework: &signer) acquires RequiredGasDeposit, AllowCustomMaxGasFlag {
        system_addresses::assert_aptos_framework(framework);
        if (config_buffer::does_exist<RequiredGasDeposit>()) {
            let new_config = config_buffer::extract_v2<RequiredGasDeposit>();
            if (exists<RequiredGasDeposit>(@aptos_framework)) {
                *borrow_global_mut<RequiredGasDeposit>(@aptos_framework) = new_config;
            } else {
                move_to(framework, new_config);
            }
        };
        if (config_buffer::does_exist<AllowCustomMaxGasFlag>()) {
            let new_config = config_buffer::extract_v2<AllowCustomMaxGasFlag>();
            if (exists<AllowCustomMaxGasFlag>(@aptos_framework)) {
                *borrow_global_mut<AllowCustomMaxGasFlag>(@aptos_framework) = new_config;
            } else {
                move_to(framework, new_config);
            }
        }
    }
```

**File:** aptos-move/aptos-vm-environment/src/prod_configs.rs (L330-347)
```rust
impl RandomnessConfig {
    /// Returns randomness config based on the current state.
    pub fn fetch(state_view: &impl StateView) -> Self {
        let randomness_api_v0_required_deposit = RequiredGasDeposit::fetch_config(state_view)
            .ok()
            .flatten()
            .unwrap_or_else(RequiredGasDeposit::default_if_missing)
            .gas_amount;
        let allow_rand_contract_custom_max_gas = AllowCustomMaxGasFlag::fetch_config(state_view)
            .ok()
            .flatten()
            .unwrap_or_else(AllowCustomMaxGasFlag::default_if_missing)
            .value;
        Self {
            randomness_api_v0_required_deposit,
            allow_rand_contract_custom_max_gas,
        }
    }
```
