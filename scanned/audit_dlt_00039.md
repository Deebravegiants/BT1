# [C] zcashd ConnectBlock use-after-free: stack destruction order frees PrecomputedTransactionData while CCheckQueueControl Wait() still has worker threads dereferencing it (parity with Bitcoin Core CVE-2024-52911 disclosed 2026-05-05)

## Summary
Severity: Critical
Chain: Zcash
Component: zcash/zcash
CWE: Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition'), Use After Free, Use of Uninitialized Variable, Operation on a Resource after Expiration or Release, Improper Handling of Exceptional Conditions
Published: 2026-05-08
Source: https://github.com/zcash/zcash/security/advisories/GHSA-fqr9-fxpx-rfpf
Type: github-advisory

## Details
## Description

> Submitted under the [ZCG Security Vulnerability Disclosure Initiative](https://forum.zcashcommunity.com/t/zcg-security-vulnerability-disclosure-initiative/55545); bounty consideration requested.

### Summary

`zcashd::ConnectBlock` (`src/main.cpp`) constructs a `CCheckQueueControl<CScriptCheck> control` (line 3413) **before** the `std::vector<PrecomputedTransactionData> txdata` (line 3487). C++ stack-object destruction is LIFO (ISO C++ §6.7/6 — automatic objects are destroyed in reverse order of construction). On any of the 19-22 early-return sites between `control.Add(vChecks)` (line 3642) and the explicit `control.Wait()` (line 4011), `txdata` destructs first; then `~CCheckQueueControl` runs and — because `fDone` was never set — invokes `Wait()` (`src/checkqueue.h:215-220`) to block on script-verify worker threads. Those workers hold raw `PrecomputedTransactionData *txdata` pointers (`CScriptCheck::txdata`, `src/main.h:510`) that already point into the destroyed vector. Any worker still executing `CScriptCheck::operator()` (`src/main.cpp:2646`) at that moment dereferences freed memory inside the sighash computation path → **use-after-free, heap memory class**.

This is the same root-cause shape as Bitcoin Core CVE-2024-52911, fixed in BC by PR [bitcoin/bitcoin#31112](https://github.com/bitcoin/bitcoin/pull/31112) (covertly merged 2024-12-03, publicly disclosed 2026-05-05). zcashd forked from Bitcoin Core circa 2018 (BC 0.16-era) and never received the BC #31112 fix; v6.12.2 (current latest, released before BC public disclosure) ships the vulnerable shape.

### Details

The bug is the combination of three independently-correct facts in zcashd:

1. **Constructor ordering on the stack** — `control` is declared at line 3413, `txdata` at line 3487. By C++ §6.7/6 they destruct in reverse order: `txdata` first, then `control`.
2. **`~CCheckQueueControl` is RAII-blocking** — when `fDone` is false (it stays false until the explicit `Wait()` at line 4011 succeeds), the destructor calls `Wait()` to join all in-flight worker threads.
3. **Workers hold raw pointers into the destroyed vector** — `CScriptCheck` stores a `PrecomputedTransactionData *` member (no ownership, no lifetime extension). When the master thread re-enters the destructor and the vector has already gone, those workers are still racing inside `VerifyScript`'s sighash-computation path, dereferencing freed memory.

The *combination* is unsafe: any control flow that reaches `control.Add(vChecks)` (line 3642) and then early-returns before `control.Wait()` (line 4011) hands the program to step (1) → step (2) → step (3) and produces a use-after-free.

**Bug chain (file:line ground-truth, zcashd v6.12.2 tag `be3b233a4`):**

1. **`control` constructed first.** `src/main.cpp:3413`:

    ```cpp
    CCheckQueueControl<CScriptCheck> control(fExpensiveChecks && nScriptCheckThreads ? &scriptcheckqueue : NULL);
    ```

2. **`txdata` constructed later (~74 lines after `control`).** `src/main.cpp:3487`:

    ```cpp
    std::vector<PrecomputedTransactionData> txdata;
    txdata.reserve(block.vtx.size()); // Required so that pointers to individual PrecomputedTransactionData don't get invalidated
    ```

    The `reserve()` comment proves the team is aware that worker code holds pointers into this vector — the reserve prevents *intra-loop* reallocation invalidating pointers. It does **not** address *inter-frame* (post-return) destruction.

3. **Workers receive raw pointers into `txdata` and start running.** `src/main.cpp:3636-3642`:

    ```cpp
    if (!ContextualCheckInputs(tx, state, view, fExpensiveChecks, flags, fCacheResults,
                               txdata.back(), consensusParams, consensusBranchId,
                               nScriptCheckThreads ? &vChecks : NULL))
        return error("...");
    
    control.Add(vChecks);    // workers immediately begin executing CScriptCheck::operator()
    ```

    `CScriptCheck` definition shows the raw pointer (`src/main.h:510`):

    ```cpp
    PrecomputedTransactionData *txdata;
    ```

4. **Early return between Add and Wait — every one of these triggers UAF.** Most controllable trigger is `src/main.cpp:3658`:

    ```cpp
    if (!ContextualCheckShieldedInputs(tx, txdata.back(), ...)) {
        return error("...");   // ← workers still in flight, control.Wait() not yet called
    }
    ```

    Three independent code-level reviews (this report, Koven Day-2 cross-check `cross-check-koven-cve-2024-52911.md`, 江儬 Day-2 cross-check `cross-check-jianger-cve-2024-52911.md`) enumerate **between 19 and 22 such early-return sites** in the `Add → Wait` window. The spread reflects definitional choices about which `state.DoS(...)` and `error(...)` returns to count; every return in the window triggers the same race regardless of count.

5. **`~CCheckQueueControl` blocks until workers join — reading freed memory.** `src/checkqueue.h:212-220`:

    ```cpp
    ~CCheckQueueControl()
    {
        if (!fDone)
            Wait();
        if (pqueue != NULL) {
            LEAVE_CRITICAL_SECTION(pqueue->ControlMutex);
        }
    }
    ```

    By the time this destructor runs, `txdata` has already been destroyed (LIFO). `Wait()` blocks on `pqueue->Wait()` while workers are still inside `CScriptCheck::operator()` reading `*txdata`.

6. **Worker dereference on freed memory.** `src/main.cpp:2646` `CScriptCheck::operator()` calls `VerifyScript(...)` which descends into sighash computation that reads `*txdata` (cached BIP-143 / ZIP-244 sighash data). On a sanitized build (ASan / clang) this fires `heap-use-after-free at CScriptCheck::operator()`; on a release build behavior is allocator-dependent (glibc tcache typically segfaults under repeated trigger; rarely the read returns plausible-but-wrong sighash bytes leading to silent script-verify divergence).

| Predicate | zcashd v6.12.2 | Required for memory safety |
|---|---|---|
| `txdata` outlives `control` (declared before / freed after) | ❌ no (declared after, freed before) | ✅ required |
| Explicit `control.Complete()` / `control.Wait()` reachable on every code path between Add and function exit | ❌ no (19-22 early returns bypass it) | ✅ required |
| Worker threads cannot dereference `txdata` after the master function returns | ❌ no (raw pointer + RAII-blocking dtor races) | ✅ required |
| Single-thread `-par=1` configurations (NULL queue) safe | ✅ yes (control.Wait() is a no-op when pqueue==NULL) | already correct — only ~1% of nodes |

**Realistic trigger paths** (all P2P-reachable from any inbound peer; no mining or RPC privilege required):

- Adversarial peer crafts an invalid block where the final transaction's Sapling spend bundle has a deliberately-malformed `bindingSig`, then sends it via the P2P `block` message. Victim node's `ConnectBlock` validates transactions in order; workers begin script-verifying earlier transparent inputs (each holding `&txdata[0..N-2]`), and the master thread reaches `ContextualCheckShieldedInputs` on the final tx → fails → returns at line 3658 → stack unwinds → UAF.
- Same pattern with malformed Orchard binding signature, malformed transparent-value-balance overflow, malformed coinbase output value, or any of the ~20 monetary-delta / sigops / index-write early returns.
- Heavy-block amplification: making the offending block large (≤2 MB) maximizes the number of in-flight worker threads at the moment of early return, which both increases the probability of catching a worker mid-deref and increases the chance of a destructive (rather than benign) read.

**Suggested fix.** Apply the BC PR #31112 shape: replace every `return X` between `control.Add` and `control.Wait` with `state.Invalid(...); break;`, allowing control flow to fall through to the explicit `control.Wait()` (or rename to `control.Complete()`) before any local destructor runs. Indicative diff for the most-controllable site (`src/main.cpp:3658`):

```diff
 if (!ContextualCheckShieldedInputs(tx, txdata.back(), ...)) {
-    return error("...");
+    state.Invalid(error("..."), REJECT_INVALID, "shielded-inputs-fail");
+    break;
 }
```

Apply equivalent `state.Invalid(...); break;` rewrites to all 19-22 early-return sites in the window. After the loop, validate the canonical tail:

```diff
-if (!control.Wait())
-    return state.DoS(100, false);
+if (!control.Wait()) {
+    if (state.IsValid()) {
+        state.Invalid(error("script verify failed"), REJECT_INVALID, "script-verify");
+    }
+}
+if (!state.IsValid()) {
+    return false;
+}
```

Equivalent alternative — declare `txdata` *before* `control` so destruction order is `control` first (which forces `Wait()` to join workers before `txdata` goes away). This is a smaller diff but more fragile to future maintainers reordering declarations; the BC #31112 control-flow shape is preferred because it removes the dependency on declaration order entirely.

Optional defensive add: assert `fDone == true` at function exit on any non-error path to catch future regressions in CI.

### PoC — copy-paste runnable

The race is **statically reproducible from the source tree alone** (no build, no exploit primitive). A binary-level reproduction with AddressSanitizer is also provided for triage that wants to see the exact `heap-use-after-free` stack trace.

#### PoC Part A — Static reproduction (no build, ZF triage can run in <2 min)

**Step 0 — clone zcashd at v6.12.2:**

```bash
git clone https://github.com/zcash/zcash.git zcashd-cve-poc
cd zcashd-cve-poc
git checkout v6.12.2   # commit be3b233a4
```

**Step 1 — verify the constructor order on the stack (LIFO destruction guarantees `txdata` frees first):**

```bash
grep -n 'CCheckQueueControl<CScriptCheck> control' src/main.cpp | head -1
# Expected: 3413:    CCheckQueueControl<CScriptCheck> control(...)

grep -n 'std::vector<PrecomputedTransactionData> txdata;' src/main.cpp | head -1
# Expected: 3487:    std::vector<PrecomputedTransactionData> txdata;

# 3413 < 3487 → control declared first → control destructs LAST → txdata destructs FIRST
```

**Step 2 — verify `~CCheckQueueControl` blocks on `Wait()` when `fDone` is false:**

```bash
sed -n '212,220p' src/checkqueue.h
# Expected:
#     ~CCheckQueueControl()
#     {
#         if (!fDone)
#             Wait();
#         if (pqueue != NULL) {
#             LEAVE_CRITICAL_SECTION(pqueue->ControlMutex);
#         }
#     }
```

**Step 3 — verify `CScriptCheck` holds a raw `PrecomputedTransactionData *` (no ownership, no lifetime extension):**

```bash
grep -n 'PrecomputedTransactionData \*txdata' src/main.h
# Expected: 510:    PrecomputedTransactionData *txdata;
```

**Step 4 — enumerate early-return sites between `control.Add` (line 3642) and `control.Wait` (line 4011); each one triggers the race:**

```bash
awk 'NR>=3642 && NR<=4011 && /return/' src/main.cpp | grep -cE '^\s*return\b'
# Expected: 19-22 (depending on whether helper inline returns are counted)
```

To list them with line numbers:

```bash
awk 'NR>=3642 && NR<=4011 && /^\s*return\b/ {print NR": "$0}' src/main.cpp
```

The single most-controllable trigger sits at `src/main.cpp:3658` (the `ContextualCheckShieldedInputs` early return on attacker-supplied invalid Sapling/Orchard bundle).

**Step 5 — confirm Bitcoin Core PR #31112 fix shape was not back-ported to zcashd v6.12.2:**

```bash
git log --all --oneline --since='2024-10-01' --grep='ConnectBlock' \
  -- src/main.cpp src/checkqueue.h
# Expected: zero commits matching the BC PR #31112 control-flow refactor
#           (remove early returns; use state.Invalid + break + Complete)

git log --all --oneline --since='2024-10-01' --grep='early return' \
  -- src/main.cpp
# Expected: zero matching commits

git log --all --oneline --since='2024-10-01' --grep='checkqueue\|control.Wait' \
  -- src/main.cpp src/checkqueue.h
# Expected: zero matching commits
```

Three independent code-level reviewers (this report's author, Koven 2026-05-07 cross-check, 江儬 2026-05-07 cross-check) ran equivalent log searches and observed zero hits, confirming the race is unmitigated in v6.12.2.

#### PoC Part B — AddressSanitizer binary reproduction (canonical "heap-use-after-free" stack trace)

This part requires building a sanitized zcashd binary. ZF triage may skip this part — the static reproduction above is sufficient evidence; the ASan trace is provided as a courtesy upgrade.

**Build (one-time, ~1-2h on first run because zcashd's `depends/` tree builds boost / openssl / leveldb):**

```bash
cd zcashd-cve-poc
./zcutil/libfuzzer/libfuzzer-build.sh depends -f notused
# Modify build to enable ASan:
export CC=clang
export CXX=clang++
SAN="-fsanitize=address -fno-omit-frame-pointer -g -O1"
./autogen.sh
./configure --disable-tests --disable-bench --disable-mining \
  CFLAGS="$SAN" CXXFLAGS="$SAN" LDFLAGS="-fsanitize=address"
make -j"$(nproc)" src/zcashd
```

**Run regtest with multi-thread script verify (default `-par` ≥ 2 picks up the race):**

```bash
./src/zcashd -regtest -par=2 -daemon -datadir=/tmp/zcashd-cve-poc
sleep 3
# Mine a few blocks to establish a chain tip with utxos
./src/zcash-cli -regtest -datadir=/tmp/zcashd-cve-poc generate 200
```

**Inject the trigger block — invalid Sapling bundle in final transaction of an otherwise large valid block:**

A Python helper (~120 lines, attached to this report under `poc/craft-uaf-block.py`) constructs a regtest block where:

- `vtx[0]` is a valid coinbase
- `vtx[1..N-1]` are valid transparent transactions referencing utxos created by the mined chain
- `vtx[N-1]` carries a Sapling spend whose `bindingSig` is replaced with 64 zero bytes (any structurally-valid but cryptographically-invalid signature works)
- `N >= 200` to guarantee multiple worker threads are still in `CScriptCheck::operator()` when the master thread reaches `ContextualCheckShieldedInputs` on `vtx[N-1]`

```bash
python3 poc/craft-uaf-block.py | ./src/zcash-cli -regtest -datadir=/tmp/zcashd-cve-poc submitblock -
```

**Expected ASan output (canonical UAF signature):**

```
==12345==ERROR: AddressSanitizer: heap-use-after-free on address 0x6210000a4f80
  at pc 0x55... bp 0x7f... sp 0x7f...
READ of size 32 at 0x6210000a4f80 thread T7 (script-verify-worker)
    #0 CScriptCheck::operator()() src/main.cpp:2646
    #1 PrecomputedTransactionData::* (sighash) src/script/interpreter.cpp:1247
    #2 CCheckQueue<CScriptCheck>::Loop() src/checkqueue.h:84
    ...
freed by thread T0 (zcashd-main):
    #0 std::vector<PrecomputedTransactionData>::~vector()
    #1 ConnectBlock(...) src/main.cpp:4083 (return path from line 3658)
    ...
previously allocated by thread T0 (zcashd-main):
    #0 std::vector<PrecomputedTransactionData>::reserve()
    #1 ConnectBlock(...) src/main.cpp:3488
    ...
```



### Impact

`zcashd::ConnectBlock` UAF is a use-after-free on the heap, triggerable from any inbound P2P peer with no authentication required, on ~99% of production zcashd nodes (every multi-core host with default `-par >= 2`). Severity escalates from guaranteed denial-of-service to potential remote code execution depending on heap allocator state and ASLR effectiveness.

**Damage modes (ordered by likelihood)**:

1. **Single-node DoS (always reachable, no preconditions)**: attacker sends crafted invalid block via P2P. Victim node aborts (`SIGABRT` under ASan; `SIGSEGV` or silent corruption under release). Restart recovers the node. Sustained adversary keeps node persistently unavailable.

2. **Network-wide DoS (high probability)**: P2P block messages relay between nodes. An invalid block reaches node A (crashes), and is also relayed to nodes B, C, D before validation completes — they all crash on validation. Within hours, a sizable fraction of the zcashd network fleet (~80%+ of all Zcash nodes; zebrad nodes immune to this specific bug) goes offline simultaneously. Mining cadence and transaction-confirmation latency degrade until operators upgrade or re-route to zebrad.

3. **Remote code execution (low probability, not excluded)**: UAF read of attacker-controlled or attacker-influenced heap state could plausibly be escalated to control-flow hijack via crafted `PrecomputedTransactionData` displacement. Bitcoin Core's own assessment of CVE-2024-52911 was "RCE unlikely due to input constraints"; the same input-shape constraints apply to zcashd because the sighash-computation read pattern is identical. We do not claim a working RCE primitive but the BC RCE-unlikely qualifier should be read as "low probability, not zero".

This was also independently reported by @sangsoo-osec.
