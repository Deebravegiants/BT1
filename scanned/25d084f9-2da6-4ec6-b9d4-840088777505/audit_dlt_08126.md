# [?] rpc: fix DoS vector in get_output_distribution

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-10-24
Source: https://github.com/monero-project/monero/commit/e8e507f36f864c5558aaa15024673ac5cb66289f
Type: security-commit

## Details
rpc: fix DoS vector in get_output_distribution

This will prevent people spending old pre-rct outputs using a
stranger's node, which may be a good thing

## Patch
### src/rpc/core_rpc_server.cpp
```diff
@@ -3164,6 +3164,14 @@ namespace cryptonote
     if (use_bootstrap_daemon_if_necessary<COMMAND_RPC_GET_OUTPUT_DISTRIBUTION>(invoke_http_mode::JON_RPC, "get_output_distribution", req, res, r))
       return r;
 
+    const bool restricted = m_restricted && ctx;
+    if (restricted && req.amounts != std::vector<uint64_t>(1, 0))
+    {
+      error_resp.code = CORE_RPC_ERROR_CODE_RESTRICTED;
+      error_resp.message = "Restricted RPC can only get output distribution for rct outputs. Use your own node.";
+      return false;
+    }
+
     size_t n_0 = 0, n_non0 = 0;
     for (uint64_t amount: req.amounts)
       if (amount) ++n_non0; else ++n_0;
@@ -3205,6 +3213,13 @@ namespace cryptonote
     if (use_bootstrap_daemon_if_necessary<COMMAND_RPC_GET_OUTPUT_DISTRIBUTION>(invoke_http_mode::BIN, "/get_output_distribution.bin", req, res, r))
       return r;
 
+    const bool restricted = m_restricted && ctx;
+    if (restricted && req.amounts != std::vector<uint64_t>(1, 0))
+    {
+      res.status = "Restricted RPC can only get output distribution for rct outputs. Use your own node.";
+      return false;
+    }
+
     size_t n_0 = 0, n_non0 = 0;
     for (uint64_t amount: req.amounts)
       if (amount) ++n_non0; else ++n_0;
```
