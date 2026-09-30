# [?] [move-prover] Fixing unsoundness in opaque aborts_if specs.

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2020-08-12
Source: https://github.com/move-language/move/commit/a5615de34622143094fa59b07f504bc0cb614eca
Type: security-commit

## Details
[move-prover] Fixing unsoundness in opaque aborts_if specs.

Shaz discovered a very unfortunate unsoundess bugs in aborts_if specs in the presence of `pragma opaque` as part of the more general `modifies` work.

As there is no `modifies` clause in Boogie opaque procedures for `$abort_flag` and `$abort_code`, it is assumed to not change. However, the `aborts_if` spec may say that it changes, creating unsoundness.

This is a kind of emergency fix for this issue, adding the modifies clause to the boogie output, before more wrong specs are created. As a result, multiple specs now not longer verify and/or start to timeout. This are commented out for now. Fixing those cases will conflict with changes in the error work, so they are happening in this PR.

Closes: #5575

## Patch
### language/move-prover/spec-lang/src/env.rs
```diff
@@ -1896,6 +1896,11 @@ impl<'env> FunctionEnv<'env> {
         view.is_native() || self.is_pragma_true(INTRINSIC_PRAGMA, || false)
     }
 
+    /// Returns true if this function is opaque.
+    pub fn is_opaque(&self) -> bool {
+        self.is_pragma_true(OPAQUE_PRAGMA, || false)
+    }
+
     /// Returns true if this function is public.
     pub fn is_public(&self) -> bool {
         let view = self.definition_view();
```

### language/move-prover/src/bytecode_translator.rs
```diff
@@ -531,7 +531,7 @@ impl<'env> ModuleTranslator<'env> {
         for entry_point in entries {
             self.generate_function_sig(func_target, entry_point);
             if opaque {
-                emit!(self.writer, ";");
+                emitln!(self.writer, ";\nmodifies $abort_flag, $abort_code;");
             }
             let st = self.new_spec_translator(func_target.clone(), true);
             let distribution = self.generate_function_spec(&st, entry_point);
@@ -909,10 +909,14 @@ impl<'env> ModuleTranslator<'env> {
                 loc.span().start(),
             )
         };
-        let propagate_abort_from_call = || {
-            // In case of a call, we do not track the abortion point, as we want to see the
-            // abort on the instruction which caused it.
-            "if ($abort_flag) {\n  goto Abort;\n}".to_string()
+        let propagate_abort_from_call = |callee_target: &FunctionTarget<'_>| {
+            if callee_target.is_native() || callee_target.is_opaque() {
+                propagate_abort()
+            } else {
+                // In case of a call to an inlined function, we do not track the abortion point,
+                // as we want to see the abort on the primitive which caused it.
+                "if ($abort_flag) {\n  goto Abort;\n}".to_string()
+            }
         };
 
         // Translate the bytecode instruction.
@@ -1190,7 +1194,7 @@ impl<'env> ModuleTranslator<'env> {
                             // Assume that calls to this function do not abort
                             emitln!(self.writer, "assume $abort_flag == false;");
                         } else {
-                            emitln!(self.writer, &propagate_abort_from_call());
+                            emitln!(self.writer, &propagate_abort_from_call(&callee_target));
                         }
                         for s in &dest_type_assumptions {
                             emitln!(self.writer, s);
```

### language/move-prover/stackless-bytecode-generator/src/function_target.rs
```diff
@@ -128,6 +128,11 @@ impl<'env> FunctionTarget<'env> {
         self.func_env.is_native()
     }
 
+    /// Returns true if this function is opaque.
+    pub fn is_opaque(&self) -> bool {
+        self.func_env.is_opaque()
+    }
+
     /// Returns true if this function is public.
     pub fn is_public(&self) -> bool {
         self.func_env.is_public()
```

### language/stdlib/modules/DualAttestation.move
```diff
@@ -171,6 +171,8 @@ module DualAttestation {
         if (VASP::is_child(addr)) VASP::parent_address(addr) else addr
     }
     spec fun credential_address {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         aborts_if false;
         ensures result == spec_credential_address(addr);
     }
@@ -205,6 +207,8 @@ module DualAttestation {
             VASP::parent_address(payer) != VASP::parent_address(payee)
     }
     spec fun dual_attestation_required {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         pragma opaque = true;
         include DualAttestationRequiredAbortsIf<Token>;
         ensures result == spec_dual_attestation_required<Token>(payer, payee, deposit_value);
@@ -275,6 +279,8 @@ module DualAttestation {
         );
     }
     spec fun assert_signature_is_valid {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         pragma opaque = true;
         include AssertSignatureValidAbortsIf;
     }
@@ -327,6 +333,8 @@ module DualAttestation {
         }
     }
     spec fun assert_payment_ok {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         pragma opaque;
         include AssertPaymentOkAbortsIf<Currency>;
     }
```

### language/stdlib/modules/LibraAccount.move
```diff
@@ -287,6 +287,8 @@ module LibraAccount {
         );
     }
     spec fun deposit {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         include DepositAbortsIf<Token>{amount: to_deposit.value};
         include DepositEnsures<Token>{amount: to_deposit.value};
     }
@@ -350,6 +352,10 @@ module LibraAccount {
         // `preburn_address`'s `Preburn` resource to its balance
         deposit(preburn_address, preburn_address, coin, x"", x"")
     }
+    spec fun cancel_burn {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
+    }
 
     /// Helper to withdraw `amount` from the given account balance and return the withdrawn Libra<Token>
     fun withdraw_from_balance<Token>(
@@ -375,6 +381,8 @@ module LibraAccount {
         Libra::withdraw(coin, amount)
     }
     spec fun withdraw_from_balance {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         include WithdrawFromBalanceAbortsIf<Token>;
         include WithdrawFromBalanceEnsures<Token>;
     }
@@ -668,6 +676,10 @@ module LibraAccount {
         add_currencies_for_account<Token>(&new_account, add_all_currencies);
         make_account(new_account, auth_key_prefix)
     }
+    spec fun create_parent_vasp_account {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
+    }
 
     /// Create an account with the ChildVASP role at `new_account_address` with authentication key
     /// `auth_key_prefix` | `new_account_address` and a 0 balance of type `Token`. If
@@ -689,6 +701,10 @@ module LibraAccount {
         add_currencies_for_account<Token>(&new_account, add_all_currencies);
         make_account(new_account, auth_key_prefix)
     }
+    spec fun create_child_vasp_account {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
+    }
 
     ///////////////////////////////////////////////////////////////////////////
     // General purpose methods
```

### language/stdlib/modules/LibraSystem.move
```diff
@@ -145,6 +145,8 @@ module LibraSystem {
         set_validator_set(validator_set);
     }
     spec fun remove_validator {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         aborts_if !Roles::spec_has_libra_root_role_addr(Signer::spec_address_of(lr_account));
         aborts_if !LibraConfig::spec_is_published<LibraSystem>();
         aborts_if !spec_is_validator(account_address);
@@ -170,6 +172,8 @@ module LibraSystem {
         }
     }
     spec fun update_config_and_reconfigure {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         aborts_if ValidatorConfig::spec_get_operator(validator_address)
             != Signer::spec_address_of(operator_account);
         aborts_if !LibraConfig::spec_is_published<LibraSystem>();
@@ -221,6 +225,8 @@ module LibraSystem {
         *&(Vector::borrow(&validator_set.validators, *Option::borrow(&validator_index_vec))).config
     }
     spec fun get_validator_config {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         pragma opaque;
         aborts_if !LibraConfig::spec_is_published<LibraSystem>();
         aborts_if !spec_is_validator(addr);
@@ -322,6 +328,8 @@ module LibraSystem {
         Option::is_some(&get_validator_index_(validators_vec_ref, addr))
     }
     spec fun is_validator_ {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         pragma opaque;
         aborts_if false;
         ensures result == (exists v in validators_vec_ref: v.addr == addr);
```

### language/stdlib/modules/RecoveryAddress.move
```diff
@@ -43,6 +43,10 @@ module RecoveryAddress {
             RecoveryAddress { rotation_caps: Vector::singleton(rotation_cap) }
         )
     }
+    spec fun publish {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
+    }
 
     /// Rotate the authentication key of `to_recover` to `new_key`. Can be invoked by either
     /// `recovery_address` or `to_recover`.
@@ -109,6 +113,10 @@ module RecoveryAddress {
             to_recover
         );
     }
+    spec fun add_rotation_capability {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
+    }
 
     // ****************** SPECIFICATIONS *******************
 
```

### language/stdlib/modules/TransactionFee.move
```diff
@@ -145,6 +145,8 @@ module TransactionFee {
     }
 
     spec fun burn_fees {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         /// > TODO(emmazzz): We are not able to specify formally the conditions
         /// involving FixedPoint32. Here are some informal specifications:
         /// (1) aborts if CoinType is LBR and the reserve does not have enough
```

### language/stdlib/modules/VASP.move
```diff
@@ -57,6 +57,8 @@ module VASP {
         move_to(vasp, ParentVASP { num_children: 0 });
     }
     spec fun publish_parent_vasp_credential {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         aborts_if !Roles::spec_has_libra_root_role_addr(Signer::spec_address_of(lr_account));
         aborts_if !Roles::spec_has_parent_VASP_role_addr(Signer::spec_address_of(vasp));
         aborts_if spec_is_vasp(Signer::spec_address_of(vasp));
@@ -87,6 +89,8 @@ module VASP {
         move_to(child, ChildVASP { parent_vasp_addr });
     }
     spec fun publish_child_vasp_credential {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         aborts_if !Roles::spec_has_parent_VASP_role_addr(Signer::spec_address_of(parent));
         aborts_if spec_is_vasp(Signer::spec_address_of(child));
         aborts_if !spec_is_parent_vasp(Signer::spec_address_of(parent));
@@ -121,6 +125,8 @@ module VASP {
         }
     }
     spec fun parent_address {
+        // TODO: reactivate after aborts_if soundness fix.
+        pragma verify = false;
         pragma opaque = true;
         ensures result == spec_parent_address(addr);
     }
```

### language/stdlib/modules/doc/DualAttestation.md
```diff
@@ -744,7 +744,8 @@ Spec version of
 
 
 
-<pre><code><b>aborts_if</b> <b>false</b>;
+<pre><code>pragma verify = <b>false</b>;
+<b>aborts_if</b> <b>false</b>;
 <b>ensures</b> result == <a href="#0x1_DualAttestation_spec_credential_address">spec_credential_address</a>(addr);
 </code></pre>
 
@@ -776,7 +777,8 @@ Spec version of
 
 
 
-<pre><code>pragma opaque = <b>true</b>;
+<pre><code>pragma verify = <b>false</b>;
+pragma opaque = <b>true</b>;
 <b>include</b> <a href="#0x1_DualAttestation_DualAttestationRequiredAbortsIf">DualAttestationRequiredAbortsIf</a>&lt;Token&gt;;
 <b>ensures</b> result == <a href="#0x1_DualAttestation_spec_dual_attestation_required">spec_dual_attestation_required</a>&lt;Token&gt;(payer, payee, deposit_value);
 </code></pre>
@@ -871,7 +873,8 @@ Uninterpreted function for
 
 
 
-<pre><code>pragma opaque = <b>true</b>;
+<pre><code>pragma verify = <b>false</b>;
+pragma opaque = <b>true</b>;
 <b>include</b> <a href="#0x1_DualAttestation_AssertSignatureValidAbortsIf">AssertSignatureValidAbortsIf</a>;
 </code></pre>
 
@@ -929,7 +932,8 @@ Returns true if signature is valid.
 
 
 
-<pre><code>pragma opaque;
+<pre><code>pragma verify = <b>false</b>;
+pragma opaque;
 <b>include</b> <a href="#0x1_DualAttestation_AssertPaymentOkAbortsIf">AssertPaymentOkAbortsIf</a>&lt;Currency&gt;;
 </code></pre>
 
```

### language/stdlib/modules/doc/LibraAccount.md
```diff
@@ -60,11 +60,14 @@
 -  [Specification](#0x1_LibraAccount_Specification)
     -  [Function `should_track_limits_for_account`](#0x1_LibraAccount_Specification_should_track_limits_for_account)
     -  [Function `deposit`](#0x1_LibraAccount_Specification_deposit)
+    -  [Function `cancel_burn`](#0x1_LibraAccount_Specification_cancel_burn)
     -  [Function `withdraw_from_balance`](#0x1_LibraAccount_Specification_withdraw_from_balance)
     -  [Function `rotate_authentication_key`](#0x1_LibraAccount_Specification_rotate_authentication_key)
     -  [Function `extract_key_rotation_capability`](#0x1_LibraAccount_Specification_extract_key_rotation_capability)
     -  [Function `restore_key_rotation_capability`](#0x1_LibraAccount_Specification_restore_key_rotation_capability)
     -  [Function `create_designated_dealer`](#0x1_LibraAccount_Specification_create_designated_dealer)
+    -  [Function `create_parent_vasp_account`](#0x1_LibraAccount_Specification_create_parent_vasp_account)
+    -  [Function `create_child_vasp_account`](#0x1_LibraAccount_Specification_create_child_vasp_account)
 
 
 
@@ -2040,7 +2043,8 @@ a writeset transaction is committed.
 
 
 
-<pre><code><b>include</b> <a href="#0x1_LibraAccount_DepositAbortsIf">DepositAbortsIf</a>&lt;Token&gt;{amount: to_deposit.value};
+<pre><code>pragma verify = <b>false</b>;
+<b>include</b> <a href="#0x1_LibraAccount_DepositAbortsIf">DepositAbortsIf</a>&lt;Token&gt;{amount: to_deposit.value};
 <b>include</b> <a href="#0x1_LibraAccount_DepositEnsures">DepositEnsures</a>&lt;Token&gt;{amount: to_deposit.value};
 </code></pre>
 
@@ -2093,6 +2097,22 @@ a writeset transaction is committed.
 
 
 
+<a name="0x1_LibraAccount_Specification_cancel_burn"></a>
+
+### Function `cancel_burn`
+
+
+<pre><code><b>public</b> <b>fun</b> <a href="#0x1_LibraAccount_cancel_burn">cancel_burn</a>&lt;Token&gt;(account: &signer, preburn_address: address)
+</code></pre>
+
+
+
+
+<pre><code>pragma verify = <b>false</b>;
+</code></pre>
+
+
+
 <a name="0x1_LibraAccount_Specification_withdraw_from_balance"></a>
 
 ### Function `withdraw_from_balance`
@@ -2104,7 +2124,8 @@ a writeset transaction is committed.
 
 
 
-<pre><code><b>include</b> <a href="#0x1_LibraAccount_WithdrawFromBalanceAbortsIf">WithdrawFromBalanceAbortsIf</a>&lt;Token&gt;;
+<pre><code>pragma verify = <b>false</b>;
+<b>include</b> <a href="#0x1_LibraAccount_WithdrawFromBalanceAbortsIf">WithdrawFromBalanceAbortsIf</a>&lt;Token&gt;;
 <b>include</b> <a href="#0x1_LibraAccount_WithdrawFromBalanceEnsures">WithdrawFromBalanceEnsures</a>&lt;Token&gt;;
 </code></pre>
 
@@ -2227,6 +2248,38 @@ a writeset transaction is committed.
 
 
 
+<pre><code>pragma verify = <b>false</b>;
+</code></pre>
+
+
+
+<a name="0x1_LibraAccount_Specification_create_parent_vasp_account"></a>
+
+### Function `create_parent_vasp_account`
+
+
+<pre><code><b>public</b> <b>fun</b> <a href="#0x1_LibraAccount_create_parent_vasp_account">create_parent_vasp_account</a>&lt;Token&gt;(creator_account: &signer, new_account_address: address, auth_key_prefix: vector&lt;u8&gt;, human_name: vector&lt;u8&gt;, base_url: vector&lt;u8&gt;, compliance_public_key: vector&lt;u8&gt;, add_all_currencies: bool)
+</code></pre>
+
+
+
+
+<pre><code>pragma verify = <b>false</b>;
+</code></pre>
+
+
+
+<a name="0x1_LibraAccount_Specification_create_child_vasp_account"></a>
+
+### Function `create_child_vasp_account`
+
+
+<pre><code><b>public</b> <b>fun</b> <a href="#0x1_LibraAccount_create_child_vasp_account">create_child_vasp_account</a>&lt;Token&gt;(parent: &signer, new_account_address: address, auth_key_prefix: vector&lt;u8&gt;, add_all_currencies: bool)
+</code></pre>
+
+
+
+
 <pre><code>pragma verify = <b>false</b>;
 </code></pre>
 
```

### language/stdlib/modules/doc/LibraSystem.md
```diff
@@ -676,7 +676,8 @@ Validators have unique addresses.
 
 
 
-<pre><code><b>aborts_if</b> !<a href="Roles.md#0x1_Roles_spec_has_libra_root_role_addr">Roles::spec_has_libra_root_role_addr</a>(<a href="Signer.md#0x1_Signer_spec_address_of">Signer::spec_address_of</a>(lr_account));
+<pre><code>pragma verify = <b>false</b>;
+<b>aborts_if</b> !<a href="Roles.md#0x1_Roles_spec_has_libra_root_role_addr">Roles::spec_has_libra_root_role_addr</a>(<a href="Signer.md#0x1_Signer_spec_address_of">Signer::spec_address_of</a>(lr_account));
 <b>aborts_if</b> !<a href="LibraConfig.md#0x1_LibraConfig_spec_is_published">LibraConfig::spec_is_published</a>&lt;<a href="#0x1_LibraSystem">LibraSystem</a>&gt;();
 <b>aborts_if</b> !<a href="#0x1_LibraSystem_spec_is_validator">spec_is_validator</a>(account_address);
 <b>ensures</b> !<a href="#0x1_LibraSystem_spec_is_validator">spec_is_validator</a>(account_address);
@@ -695,7 +696,8 @@ Validators have unique addresses.
 
 
 
-<pre><code><b>aborts_if</b> <a href="ValidatorConfig.md#0x1_ValidatorConfig_spec_get_operator">ValidatorConfig::spec_get_operator</a>(validator_address)
+<pre><code>pragma verify = <b>false</b>;
+<b>aborts_if</b> <a href="ValidatorConfig.md#0x1_ValidatorConfig_spec_get_operator">ValidatorConfig::spec_get_operator</a>(validator_address)
     != <a href="Signer.md#0x1_Signer_spec_address_of">Signer::spec_address_of</a>(operator_account);
 <b>aborts_if</b> !<a href="LibraConfig.md#0x1_LibraConfig_spec_is_published">LibraConfig::spec_is_published</a>&lt;<a href="#0x1_LibraSystem">LibraSystem</a>&gt;();
 <b>aborts_if</b> !<a href="#0x1_LibraSystem_spec_is_validator">spec_is_validator</a>(validator_address);
@@ -773,7 +775,8 @@ Validators have unique addresses.
 
 
 
-<pre><code>pragma opaque;
+<pre><code>pragma verify = <b>false</b>;
+pragma opaque;
 <b>aborts_if</b> !<a href="LibraConfig.md#0x1_LibraConfig_spec_is_published">LibraConfig::spec_is_published</a>&lt;<a href="#0x1_LibraSystem">LibraSystem</a>&gt;();
 <b>aborts_if</b> !<a href="#0x1_LibraSystem_spec_is_validator">spec_is_validator</a>(addr);
 </code></pre>
@@ -874,7 +877,8 @@ Validators have unique addresses.
 
 
 
-<pre><code>pragma opaque;
+<pre><code>pragma verify = <b>false</b>;
+pragma opaque;
 <b>aborts_if</b> <b>false</b>;
 <b>ensures</b> result == (exists v in validators_vec_ref: v.addr == addr);
 </code></pre>
```
