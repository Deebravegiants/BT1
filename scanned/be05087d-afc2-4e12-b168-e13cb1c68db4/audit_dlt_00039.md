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

_Trimmed to 38 lines — full report: https://github.com/zcash/zcash/security/advisories/GHSA-fqr9-fxpx-rfpf_
