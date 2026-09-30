# [?] A companion Leap changes for fixing WASM memory exhaustion

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-07-01
Source: https://github.com/AntelopeIO/leap/commit/7bcebcaa0f9794ff0a531def5b69ccf08346127e
Type: security-commit

## Details
A companion Leap changes for fixing WASM memory exhaustion

## Patch
### libraries/chain/webassembly/runtimes/eos-vm.cpp
```diff
@@ -247,7 +247,7 @@ std::unique_ptr<wasm_instantiated_module_interface> eos_vm_runtime<Impl>::instan
       wasm_code_ptr code((uint8_t*)code_bytes, code_size);
       apply_options options = { .max_pages = 65536,
                                 .max_call_depth = 0 };
-      std::unique_ptr<backend_t> bkend = std::make_unique<backend_t>(code, code_size, nullptr, options);
+      std::unique_ptr<backend_t> bkend = std::make_unique<backend_t>(code, code_size, nullptr, options, false); // uses 2-passes parsing
       eos_vm_host_functions_t::resolve(bkend->get_module());
       return std::make_unique<eos_vm_instantiated_module<Impl>>(this, std::move(bkend));
    } catch(eosio::vm::exception& e) {
@@ -273,7 +273,7 @@ std::unique_ptr<wasm_instantiated_module_interface> eos_vm_profile_runtime::inst
       wasm_code_ptr code((uint8_t*)code_bytes, code_size);
       apply_options options = { .max_pages = 65536,
                                 .max_call_depth = 0 };
-      std::unique_ptr<backend_t> bkend = std::make_unique<backend_t>(code, code_size, nullptr, options);
+      std::unique_ptr<backend_t> bkend = std::make_unique<backend_t>(code, code_size, nullptr, options, false); // uses 2-passes parsing
       eos_vm_host_functions_t::resolve(bkend->get_module());
       return std::make_unique<eos_vm_profiling_module>(std::move(bkend), code_bytes, code_size);
    } catch(eosio::vm::exception& e) {
```
