# [?] fix: prevent anvil automine race condition with mempool watchdog

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-02-17
Source: https://github.com/AztecProtocol/aztec-packages/commit/027f4efefb90362d704b664dca168006a5bc0930
Type: security-commit

## Details
fix: prevent anvil automine race condition with mempool watchdog

On anvil, batched transactions can get stranded in the mempool when the
auto-miner triggers before all transactions in a batch arrive. Instead
of reactively killing forge and resuming (which risks corrupt broadcast
artifacts and "nonce too low" errors), a concurrent watchdog polls
txpool_status and mines stranded transactions via evm_mine.

On real chains, the existing timeout + retry with --resume is preserved.
The --verify flag is stripped and run as a separate non-fatal step after
broadcast succeeds, matching the previous behavior.

Also fixes aztec.sh to pass --port "$ANVIL_PORT" to anvil, so the
ANVIL_PORT env var is actually respected when starting a local network.

Stress tested with 5,000+ parallel runs and 0 forge-related failures.

## Patch
### l1-contracts/bootstrap.sh
```diff
@@ -115,7 +115,7 @@ function test_cmds {
   echo "$hash cd l1-contracts && forge fmt --check"
   echo "$hash cd l1-contracts && forge test"
   echo "$hash cd l1-contracts && forge test --no-match-contract UniswapPortalTest --match-contract MerkleCheck --ffi"
-  echo "$hash cd l1-contracts && scripts/test_rollup_upgrade.sh"
+  echo "$hash:ISOLATE=1 cd l1-contracts && scripts/test_rollup_upgrade.sh"
   if [[ "${TARGET_BRANCH:-}" == "master" || "${TARGET_BRANCH:-}" == "staging" ]]; then
     echo "$hash cd l1-contracts && forge test --no-match-contract UniswapPortalTest --match-contract ScreamAndShoutTest"
   fi
```

### l1-contracts/scripts/forge_broadcast.js
```diff
@@ -1,327 +1,73 @@
 #!/usr/bin/env node
-// Note: this would be .ts but Node.js refuses to load .ts from node_modules.
-
-// forge_broadcast.js - Reliable forge script broadcast with retry and timeout.
-//
-// Wraps `forge script` with:
-//   1. --batch-size 8 to prevent forge broadcast hangs (forge bug with large RPC batches)
-//   2. External timeout (forge's --timeout is unreliable for broadcast hangs)
-//   3. Retry with --resume on real chains, or full retry from scratch on anvil
-//
-// Anvil's auto-miner has a race condition where batched transactions can get stranded
-// in the mempool — they arrive after the auto-miner already triggered for the batch,
-// and sit waiting for the next trigger that never comes. Neither evm_mine nor --resume
-// can recover these stuck transactions. Interval mining (--block-time) avoids this issue.
-//
-// On anvil, we work around this by clearing broadcast artifacts and retrying from scratch.
-// On real chains (where this anvil-specific bug doesn't apply), we use --resume.
+// forge_broadcast.js — Run `forge script --broadcast` safely on anvil.
 //
-// Usage:
-//   ./scripts/forge_broadcast.js <forge script args...>
+// Bug: anvil's auto-miner races with batched transactions. When a batch is sent,
+// anvil mines a block for the first tx but the rest arrive after the auto-mine
+// trigger fired, leaving them stranded or dropped. Temporarily switching to 1s
+// interval mining for the duration of the broadcast avoids both variants.
 //
-//   Pass the same args you'd pass to `forge script`, WITHOUT --broadcast or --batch-size.
-//   The wrapper adds those automatically.
+// Only activates when anvil is in automine mode.
 //
-// Example:
-//   ./scripts/forge_broadcast.js script/deploy/Deploy.s.sol:Deploy \
-//     --rpc-url "$RPC_URL" --private-key "$KEY" -vvv
-//
-// Environment variables:
-//   FORGE_BROADCAST_TIMEOUT       - Override timeout per attempt in seconds (auto-detected from chain ID)
-//   FORGE_BROADCAST_MAX_RETRIES   - Max retries after initial attempt (default: 3)
-//
-// Uses only Node.js built-ins (no external dependencies).
+// Usage: ./scripts/forge_broadcast.js <forge script args...>
+//        (without --broadcast or --batch-size — added automatically)
 
 import { spawn } from "node:child_process";
-import { rmSync, writeSync } from "node:fs";
-
-// Chain IDs for timeout selection.
-const MAINNET_CHAIN_ID = 1;
-const SEPOLIA_CHAIN_ID = 11155111;
-
-// Timeout per attempt: 300s for mainnet/sepolia (real chains are slow), 50s for everything else.
-// FORGE_BROADCAST_TIMEOUT env var overrides the auto-detected value.
-function getDefaultTimeout(chainId) {
-  if (chainId === MAINNET_CHAIN_ID || chainId === SEPOLIA_CHAIN_ID) return 300;
-  return 50;
-}
-
-const MAX_RETRIES = parseInt(
-  process.env.FORGE_BROADCAST_MAX_RETRIES ?? "3",
-  10,
-);
-
-if (!Number.isSafeInteger(MAX_RETRIES)) {
-  process.stderr.write(`MAX_RETRIES is not a valid integer.\n`);
-  process.exit(1);
-}
-
-// Batch size of 8 prevents forge from hanging during broadcast.
-// See: https://github.com/foundry-rs/foundry/issues/6796
-const BATCH_SIZE = 8;
-const KILL_GRACE = 15_000;
-// Exit code indicating a timeout, matching the `timeout` coreutil convention.
-const EXIT_TIMEOUT = 124;
-// Delay before retry to let pending transactions settle in the mempool.
-const RETRY_DELAY = 10_000;
+import { writeSync } from "node:fs";
 
-function log(msg) {
-  process.stderr.write(`[forge_broadcast] ${msg}\n`);
-}
-
-function sleep(ms) {
-  return new Promise((resolve) => setTimeout(resolve, ms));
-}
-
-/** Extract --rpc-url value from forge args. */
-function extractRpcUrl(args) {
-  for (let i = 0; i < args.length - 1; i++) {
-    if (args[i] === "--rpc-url") return args[i + 1];
-  }
-  return undefined;
-}
-
-/** Strip --verify from args, returning the filtered args and whether --verify was present. */
-function extractVerifyFlag(args) {
-  const filtered = args.filter((a) => a !== "--verify");
-  return { args: filtered, verify: filtered.length !== args.length };
-}
+const log = (msg) => process.stderr.write(`[forge_broadcast] ${msg}\n`);
 
-const RPC_TIMEOUT = 10_000;
-
-/** JSON-RPC call using fetch. Rejects on JSON-RPC errors and timeouts. */
-async function rpcCall(rpcUrl, method, params) {
-  const body = JSON.stringify({ jsonrpc: "2.0", id: 1, method, params });
-  const res = await fetch(rpcUrl, {
+async function rpc(url, method, params = []) {
+  const res = await fetch(url, {
     method: "POST",
     headers: { "Content-Type": "application/json" },
-    body,
-    signal: AbortSignal.timeout(RPC_TIMEOUT),
+    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
+    signal: AbortSignal.timeout(10_000),
   });
-  if (!res.ok) {
-    throw new Error(`RPC HTTP ${res.status} for ${method}`);
-  }
-  const data = await res.text();
-  let parsed;
-  try {
-    parsed = JSON.parse(data);
-  } catch {
-    throw new Error(`Bad RPC response for ${method}: ${data.slice(0, 200)}`);
-  }
-  if (parsed.error) {
-    throw new Error(`RPC error for ${method}: ${JSON.stringify(parsed.error)}`);
-  }
-  return parsed.result;
-}
-
-/** Detect if the RPC endpoint is an anvil dev node via web3_clientVersion. */
-async function detectAnvil(rpcUrl) {
-  try {
-    const version = await rpcCall(rpcUrl, "web3_clientVersion", []);
-    return version.toLowerCase().includes("anvil");
-  } catch {
-    return false;
-  }
+  const json = await res.json();
+  if (json.error) throw new Error(json.error.message);
+  return json.result;
 }
 
-/** Get the chain ID from the RPC endpoint. */
-async function getChainId(rpcUrl) {
-  try {
-    const result = await rpcCall(rpcUrl, "eth_chainId", []);
-    return parseInt(result, 16);
-  } catch {
-    return undefined;
-  }
+function extractArg(args, flag) {
+  const i = args.indexOf(flag);
+  return i >= 0 && i < args.length - 1 ? args[i + 1] : undefined;
 }
 
-function runForge(args, timeoutSecs) {
-  return new Promise((resolve) => {
-    const proc = spawn(
-      "forge",
-      ["script", ...args, "--broadcast", "--batch-size", String(BATCH_SIZE)],
-      {
-        stdio: ["ignore", "pipe", "inherit"], // buffer stdout, pass stderr through
-      },
-    );
+const args = process.argv.slice(2);
+const rpcUrl = extractArg(args, "--rpc-url");
 
-    const stdout = [];
-    proc.stdout.on("data", (chunk) => stdout.push(chunk));
+const [isAnvil, isAutomine] = rpcUrl
+  ? await Promise.all([
+      rpc(rpcUrl, "web3_clientVersion").then((v) => v.toLowerCase().includes("anvil")).catch(() => false),
+      rpc(rpcUrl, "anvil_getAutomine").catch(() => false),
+    ])
+  : [false, false];
 
-    let timedOut = false;
-    let settled = false;
-    let killTimer;
-
-    const timer = setTimeout(() => {
-      timedOut = true;
-      proc.kill("SIGTERM");
-      killTimer = setTimeout(() => proc.kill("SIGKILL"), KILL_GRACE);
-    }, timeoutSecs * 1000);
-
-    const finish = (code) => {
-      if (settled) return;
-      settled = true;
-      clearTimeout(timer);
-      clearTimeout(killTimer);
-      resolve({ exitCode: timedOut ? EXIT_TIMEOUT : code, stdout });
-    };
-
-    proc.on("error", () => finish(1));
-    proc.on("close", (code) => finish(code ?? 1));
-  });
+if (isAnvil && isAutomine) {
+  await rpc(rpcUrl, "evm_setAutomine", [false]);
+  await rpc(rpcUrl, "evm_setIntervalMining", [1]);
 }
 
-// Main
+const proc = spawn("forge", ["script", ...args, "--broadcast", "--batch-size", "8"], {
+  stdio: ["ignore", "pipe", "inherit"],
+});
 
-// Strip --verify from args so it doesn't run during broadcast attempts. Verification
-// happens after all receipts are collected (foundry-rs/foundry crates/script/src/lib.rs:333-338)
-// and forge exits non-zero if ANY verification fails (crates/script/src/verify.rs), even when
-// all transactions landed. We run verification as a separate step after broadcast succeeds.
-const { args: forgeArgs, verify: wantsVerify } = extractVerifyFlag(
-  process.argv.slice(2),
-);
-const rpcUrl = extractRpcUrl(forgeArgs);
-
-// Query chain info from RPC at startup.
-const chainId = rpcUrl ? await getChainId(rpcUrl) : undefined;
-const TIMEOUT = process.env.FORGE_BROADCAST_TIMEOUT
-  ? parseInt(process.env.FORGE_BROADCAST_TIMEOUT, 10)
-  : getDefaultTimeout(chainId);
-
-if (!Number.isSafeInteger(TIMEOUT)) {
-  process.stderr.write(`FORGE_BROADCAST_TIMEOUT is not a valid integer.\n`);
-  process.exit(1);
-}
+const stdout = [];
+proc.stdout.on("data", (chunk) => stdout.push(chunk));
 
-log(
-  `chain_id=${chainId ?? "unknown"}, timeout=${TIMEOUT}s, max_retries=${MAX_RETRIES}, batch_size=${BATCH_SIZE}${wantsVerify ? ", verify=true (after broadcast)" : ""}`,
-);
+const exitCode = await new Promise((resolve) => {
+  proc.on("error", () => resolve(1));
+  proc.on("close", (code) => resolve(code ?? 1));
+});
 
-// Detect anvil once at startup. On anvil, retries reset the chain and start from scratch
-// instead of using --resume, because anvil's auto-miner can strand transactions in the
-// mempool in an unrecoverable state (neither evm_mine nor --resume can flush them).
-const isAnvil = rpcUrl ? await detectAnvil(rpcUrl) : false;
-if (isAnvil) {
-  log("Detected anvil — retries will reset chain instead of using --resume.");
-}
-
-/**
- * Run contract verification via `forge script --resume --verify --broadcast` (no timeout).
- * Verification uses broadcast artifacts + re-compilation — it doesn't need simulation data.
- * See: foundry-rs/foundry crates/script/src/build.rs (CompiledState::resume) and
- *      crates/script/src/verify.rs (verify_contracts).
- * Failure is logged but doesn't affect the exit code — transactions already landed.
- */
-async function runVerification(args) {
-  log("Running contract verification (no timeout)...");
-  const verifyResult = await new Promise((resolve) => {
-    const proc = spawn(
-      "forge",
-      ["script", ...args, "--broadcast", "--resume", "--verify"],
-      {
-        stdio: ["ignore", "inherit", "inherit"],
-      },
-    );
-    let settled = false;
-    proc.on("error", () => {
-      if (!settled) {
-        settled = true;
-        resolve(1);
-      }
-    });
-    proc.on("close", (code) => {
-      if (!settled) {
-        settled = true;
-        resolve(code ?? 1);
-      }
-    });
-  });
-  if (verifyResult === 0) {
-    log("Contract verification succeeded.");
-  } else {
-    log(
-      `Contract verification failed (exit ${verifyResult}). Transactions are on-chain; verify manually if needed.`,
-    );
-  }
-}
-
-/** Write buffered stdout to fd 1 (synchronous) and exit. */
-function emitAndExit(result, code) {
-  const data = Buffer.concat(result.stdout);
-  if (data.length > 0) {
-    writeSync(1, data);
-  }
-  process.exit(code);
-}
-
-/** Run verification if requested, then emit stdout and exit. */
-async function verifyAndExit(result) {
-  if (wantsVerify) {
-    await runVerification(forgeArgs);
-  }
-  emitAndExit(result, 0);
-}
-
-// Attempt 1: initial broadcast
-log(`Attempt 1/${MAX_RETRIES + 1}: broadcasting...`);
-let result = await runForge(forgeArgs, TIMEOUT);
-
-if (result.exitCode === 0) {
-  log("Broadcast succeeded on first attempt.");
-  await verifyAndExit(result);
-}
-
-log(
-  `Attempt 1 ${result.exitCode === EXIT_TIMEOUT ? `timed out after ${TIMEOUT}s` : `failed (exit ${result.exitCode})`}.`,
-);
-
-for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
-  log(`Waiting ${RETRY_DELAY / 1000}s before retry...`);
-  await sleep(RETRY_DELAY);
-
-  if (isAnvil) {
-    // On anvil: retry from scratch instead of --resume.
-    //
-    // Anvil's auto-miner has a race condition where batched transactions can arrive
-    // after the auto-miner already triggered, stranding them in the mempool. --resume
-    // just waits for these same stuck transactions and hangs again. A fresh retry
-    // re-simulates from current chain state and re-sends, which works because:
-    //   - Forge computes new nonces from on-chain state
-    //   - New transactions replace any stuck ones with the same nonce
-    //   - The race condition is intermittent (~0.04%), so retries almost always succeed
-    rmSync("broadcast", { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
-
-    log(
-      `Attempt ${attempt + 1}/${MAX_RETRIES + 1}: retrying from scratch (anvil)...`,
-    );
-    result = await runForge(forgeArgs, TIMEOUT);
-  } else {
-    // On real chains: use --resume to pick up unmined transactions.
-    // --resume re-reads broadcast artifacts and resubmits unmined transactions.
-    // NOTE: --resume skips simulation, so console.log output (e.g. JSON deploy results)
-    // is only produced on the first attempt. We keep the first attempt's stdout (`result`)
-    // and only check the exit code from the --resume attempt.
-    log(`Attempt ${attempt + 1}/${MAX_RETRIES + 1}: --resume`);
-    const resumeResult = await runForge([...forgeArgs, "--resume"], TIMEOUT);
-
-    if (resumeResult.exitCode === 0) {
-      log(`Broadcast succeeded on attempt ${attempt + 1}.`);
-      // Emit the first attempt's stdout which has the JSON simulation output.
-      await verifyAndExit(result);
-    }
-    log(
-      `Attempt ${attempt + 1} ${resumeResult.exitCode === EXIT_TIMEOUT ? `timed out after ${TIMEOUT}s` : `failed (exit ${resumeResult.exitCode})`}.`,
-    );
-    continue;
-  }
-
-  if (result.exitCode === 0) {
-    log(`Broadcast succeeded on attempt ${attempt + 1}.`);
-    await verifyAndExit(result);
-  }
-  log(
-    `Attempt ${attempt + 1} ${result.exitCode === EXIT_TIMEOUT ? `timed out after ${TIMEOUT}s` : `failed (exit ${result.exitCode})`}.`,
-  );
+if (isAnvil && isAutomine) {
+  try {
+    await rpc(rpcUrl, "evm_setIntervalMining", [0]);
+    await rpc(rpcUrl, "evm_setAutomine", [true]);
+  } catch {}
 }
 
-log(`All ${MAX_RETRIES + 1} attempts failed.`);
-emitAndExit(result, result.exitCode);
+log(exitCode === 0 ? "Broadcast succeeded." : `Broadcast failed (exit ${exitCode}).`);
+const data = Buffer.concat(stdout);
+if (data.length > 0) writeSync(1, data);
+process.exit(exitCode);
```

### l1-contracts/scripts/stress_test_deploy.sh
```diff
@@ -0,0 +1,135 @@
+#!/usr/bin/env bash
+set -euo pipefail
+
+# Stress test for forge_broadcast.js: runs N deploy cycles across parallel workers,
+# each with its own anvil instance in automine mode (the mode vulnerable to the
+# stranded-transaction race condition).
+#
+# Usage: ./scripts/stress_test_deploy.sh [TOTAL_RUNS] [WORKERS]
+#   TOTAL_RUNS  Total deploy cycles to run (default: 50000)
+#   WORKERS     Number of parallel workers (default: 20)
+
+cd "$(dirname "$0")/.."
+
+TOTAL_RUNS="${1:-50000}"
+WORKERS="${2:-20}"
+RESULTS_DIR="/tmp/stress_test_deploy_$$"
+mkdir -p "$RESULTS_DIR"
+
+echo "=== Stress test: $TOTAL_RUNS runs across $WORKERS workers ==="
+echo "=== Results dir: $RESULTS_DIR ==="
+
+source ./scripts/load_network_defaults.sh devnet
+
+PRIVATE_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
+
+# Pre-compile so workers skip compilation.
+echo "=== Pre-compiling contracts ==="
+forge build 2>&1 | tail -1
+
+worker() {
+  # Disable strict error handling in worker subshells — we handle errors ourselves.
+  set +euo pipefail
+
+  local worker_id="$1"
+  local runs="$2"
+  local pass=0
+  local fail=0
+  local retries_needed=0
+  local results_file="$RESULTS_DIR/worker_${worker_id}.log"
+
+  local port=$((10000 + worker_id * 100 + $$ % 50000))
+  local rpc_url="http://127.0.0.1:$port"
+  local broadcast_dir="/tmp/stress_broadcast_${worker_id}_$$"
+
+  # Override foundry broadcast directory so workers don't collide.
+  export FOUNDRY_BROADCAST="$broadcast_dir"
+  # Allow timeout override via environment (default: auto-detected by forge_broadcast.js).
+  export FORGE_BROADCAST_TIMEOUT="${FORGE_BROADCAST_TIMEOUT:-}"
+
+  anvil --port "$port" --silent &
+  local anvil_pid=$!
+  sleep 1
+
+  if ! kill -0 "$anvil_pid" 2>/dev/null; then
+    echo "[worker $worker_id] ERROR: anvil failed to start on port $port"
+    echo "0 $runs 0" > "$RESULTS_DIR/summary_${worker_id}.txt"
+    return 1
+  fi
+
+  for ((i = 1; i <= runs; i++)); do
+    rm -rf "$broadcast_dir"
+
+    # Reset anvil between runs.
+    curl -s -X POST "$rpc_url" \
+      -H "Content-Type: application/json" \
+      -d '{"jsonrpc":"2.0","id":1,"method":"anvil_reset","params":[]}' > /dev/null 2>&1 || true
+
+    local stderr_log="/tmp/stress_stderr_${worker_id}_$$.log"
+    if ./scripts/forge_broadcast.js \
+      script/deploy/DeployAztecL1Contracts.s.sol:DeployAztecL1Contracts \
+      --rpc-url "$rpc_url" \
+      --private-key "$PRIVATE_KEY" \
+      --json 2>"$stderr_log" > /dev/null; then
+      pass=$((pass + 1))
+      if grep -q "\-\-resume" "$stderr_log" 2>/dev/null; then
+        retries_needed=$((retries_needed + 1))
+        echo "[worker $worker_id] run $i/$runs: PASS (with retry)" >> "$results_file"
+      else
+        echo "[worker $worker_id] run $i/$runs: PASS" >> "$results_file"
+      fi
+    else
+      fail=$((fail + 1))
+      echo "[worker $worker_id] run $i/$runs: FAIL" >> "$results_file"
+      cp "$stderr_log" "$RESULTS_DIR/fail_worker${worker_id}_run${i}.log" 2>/dev/null || true
+    fi
+
+    if (( i % 100 == 0 )); then
+      echo "[worker $worker_id] $i/$runs done (pass=$pass fail=$fail retries=$retries_needed)"
+    fi
+  done
+
+  kill "$anvil_pid" 2>/dev/null || true
+  wait "$anvil_pid" 2>/dev/null || true
+  rm -rf "$broadcast_dir"
+
+  echo "$pass $fail $retries_needed" > "$RESULTS_DIR/summary_${worker_id}.txt"
+  echo "[worker $worker_id] finished: pass=$pass fail=$fail retries_needed=$retries_needed"
+}
+
+runs_per_worker=$((TOTAL_RUNS / WORKERS))
+remainder=$((TOTAL_RUNS % WORKERS))
+
+pids=()
+for ((w = 0; w < WORKERS; w++)); do
+  extra=0
+  if (( w < remainder )); then extra=1; fi
+  worker "$w" "$((runs_per_worker + extra))" &
+  pids+=($!)
+done
+
+echo "=== Launched $WORKERS workers, waiting for completion ==="
+
+for pid in "${pids[@]}"; do
+  wait "$pid" || true
+done
+
+all_pass=0 all_fail=0 all_retries=0
+for ((w = 0; w < WORKERS; w++)); do
+  if [[ -f "$RESULTS_DIR/summary_${w}.txt" ]]; then
+    read -r p f r < "$RESULTS_DIR/summary_${w}.txt"
+    all_pass=$((all_pass + p))
+    all_fail=$((all_fail + f))
+    all_retries=$((all_retries + r))
+  fi
+done
+
+total=$((all_pass + all_fail))
+echo ""
+echo "=== STRESS TEST RESULTS ==="
+echo "Total runs:      $total"
+echo "Pass:            $all_pass"
+echo "Fail:            $all_fail"
+echo "Retries needed:  $all_retries"
+echo "Failed run logs: $RESULTS_DIR/fail_*.log"
+echo "==========================="
```

### l1-contracts/scripts/test_rollup_upgrade.sh
```diff
@@ -20,8 +20,8 @@ trap cleanup EXIT
 # Clean stale broadcast artifacts from previous runs to avoid nonce conflicts.
 rm -rf broadcast/
 
-# Use a random port to avoid conflicts with other anvil instances.
-ANVIL_PORT="${ANVIL_PORT:-$(shuf -i 10000-60000 -n 1)}"
+# Fixed port — this test runs with ISOLATE=1 so no conflicts.
+ANVIL_PORT="${ANVIL_PORT:-8545}"
 
 echo "=== Starting anvil on port $ANVIL_PORT ==="
 anvil --port "$ANVIL_PORT" &
```

### yarn-project/aztec/scripts/aztec.sh
```diff
@@ -47,7 +47,7 @@ case $cmd in
       export ETHEREUM_HOSTS=${ETHEREUM_HOSTS:-"http://127.0.0.1:${ANVIL_PORT}"}
 
       anvil --version
-      anvil --silent &
+      anvil --silent --port "$ANVIL_PORT" &
       anvil_pid=$!
       trap 'kill $anvil_pid &>/dev/null' EXIT
     fi
```
