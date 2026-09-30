# [?] feat(dev-tools, iota-core): add double-spend safety log-audit tool for p-cool (#11987)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-06-24
Source: https://github.com/iotaledger/iota/commit/5082be69fdb5e7a2b64e4cae6da228d7d7e485d3
Type: security-commit

## Details
feat(dev-tools, iota-core): add double-spend safety log-audit tool for p-cool (#11987)

# Description of change

Adds `dev-tools/iota-private-network/scripts/log-audit/`, a tool that
reconciles validator/fullnode/stress logs from a double-spend stress run
to prove no double-spend is leaked under the white-flag (P-COOL) flow.
- in `iota-core` additional logging was added in post-consensus
validation.
## Links to any relevant issues

fixes #11602.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [x] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes

## Patch
### crates/iota-core/src/post_consensus_validation.rs
```diff
@@ -277,12 +277,15 @@ pub async fn validate_and_resolve_conflicts(
 
         // All checks passed — acquire owned-object locks in local tracking.
         let num_owned_inputs = owned_inputs.len();
-        for obj_ref in owned_inputs {
-            current_commit_locks.insert(obj_ref, digest);
+        for obj_ref in &owned_inputs {
+            current_commit_locks.insert(*obj_ref, digest);
         }
+        // Log the acquired refs, not just their count, so the winner's locks
+        // are attributable per (object_id, version).
         debug!(
             ?digest,
             num_owned_inputs,
+            owned_inputs = ?owned_inputs,
             "Transaction passed post-consensus validation, acquired all object locks"
         );
     }
```

### dev-tools/iota-private-network/scripts/log-audit/RUNBOOK.md
```diff
@@ -0,0 +1,134 @@
+# Double-Spend Workload Runbook
+
+Run the double-spend stress workload against a local IOTA private network and
+reconcile the logs with `log-audit` to prove no double-spend leaked. The
+workload submits pairs of conflicting txs that spend the same gas coin;
+white-flag must accept exactly one of each pair.
+
+**Two repos:** `iota` (node + private network + audit) and `network-benchmark`
+(the `stress` binary with the double-spend workload — it is _not_ in
+`iota/crates/iota-benchmark`).
+
+Substitute your own checkout locations for `<path-to-iota-repo>` and
+`<path-to-network-benchmark-repo>` below. The private network lives at
+`<path-to-iota-repo>/dev-tools/iota-private-network`.
+
+## 1. Build the node image (current branch)
+
+```bash
+cd <path-to-iota-repo>
+./docker/iota-node/build.sh  -t iota-node  --no-cache
+./docker/iota-tools/build.sh -t iota-tools --no-cache
+```
+
+Builds from your working tree, so the checked-out branch is what runs.
+
+## 2. Build the stress image
+
+From `network-benchmark`, with the double-spend branch checked out:
+
+```bash
+cd <path-to-network-benchmark-repo>
+./docker/stress/build.sh          # tags iotaledger/stress
+docker run --rm iotaledger/stress /usr/local/bin/stress bench --help | grep double-spend
+```
+
+## 3. Bootstrap + start the network (benchmark mode)
+
+`-b` adds the deterministic benchmark gas accounts to genesis and writes
+`benchmark.keystore`.
+
+```bash
+cd <path-to-iota-repo>/dev-tools/iota-private-network
+sudo ./bootstrap.sh -b   # default 4 validators
+# Enable the white-flag (P-COOL post-consensus owned-object locking) flow:
+export IOTA_PROTOCOL_CONFIG_OVERRIDE_ENABLE=1
+export IOTA_PROTOCOL_CONFIG_FEATURE_FLAGS_OVERRIDE_ENABLE_PCOOL_FLOW=true
+./run.sh faucet          # validators + fullnode-1 on http://127.0.0.1:9000
+```
+
+The default `RUST_LOG` (`info,iota_core=debug,...`) already emits every event
+the audit needs (conflict/winner lines from `iota_core::post_consensus_validation`).
+
+### Optional: local Grafana
+
+Bring up the bundled Grafana + Prometheus stack to watch the run live:
+
+```bash
+cd <path-to-iota-repo>/dev-tools/grafana-local
+docker compose up -d
+```
+
+Dashboards at <http://localhost:3000/dashboards>.
+
+## 4. Run the workload
+
+On the private network's Docker network so it reaches `fullnode-1` by hostname:
+
+```bash
+export PRIVNET=<path-to-iota-repo>/dev-tools/iota-private-network
+docker run -d --name stress-benchmark \
+  --network iota-private-network_iota-network \
+  -v "$PRIVNET/configs/genesis/genesis.blob:/opt/iota/config/genesis.blob:ro" \
+  -v "$PRIVNET/configs/genesis/benchmark.keystore:/opt/iota/config/iota.keystore:ro" \
+  iotaledger/stress /usr/local/bin/stress \
+    --local false \
+    --fullnode-rpc-addresses http://fullnode-1:9000 \
+    --use-fullnode-for-execution true \
+    --use-fullnode-for-reconfig true \
+    --genesis-blob-path /opt/iota/config/genesis.blob \
+    --keystore-path /opt/iota/config/iota.keystore \
+    --primary-gas-owner-id 0xf479d29837d22943aba6afc401f518a36521b990874eca784886185bd26bf681 \
+    --num-client-threads 4 --num-transfer-accounts 10 --run-duration 1800s \
+    --client-metric-host 0.0.0.0 --client-metric-port 8081 \
+    bench --target-qps 500 --in-flight-ratio 5 --num-workers 12 \
+    --transfer-object 0 --shared-counter 0 --double-spend 100 \
+    --double-spend-num-pairs 16 --double-spend-overlap-factor 2
+```
+
+Key flags: `--double-spend 100` (100% double-spend mix), `--double-spend-num-pairs`
+(distinct contested coins), `--double-spend-overlap-factor` (oversamples so both
+halves of a pair are more likely to land in the same commit). Use a shorter
+`--run-duration 120s` for a smoke test. Follow with `docker logs -f stress-benchmark`.
+
+## 5. Collect logs
+
+> **When to grab logs:** once Grafana shows a fork (e.g. diverging checkpoint /
+> round across validators) or a hang (progress flatlines), stop the containers
+> first (`docker stop validator-* fullnode-1 stress-benchmark`) and then extract
+> the logs below — this freezes the state at the incident.
+
+The audit auto-discovers `validator-*.log` (required), `stress*.log`, and
+`fullnode-*.log` (opt-in) in one directory:
+
+```bash
+mkdir -p /tmp/ds-logs && cd /tmp/ds-logs
+for i in 1 2 3 4; do docker logs validator-$i > validator-$i.log 2>&1; done
+docker logs stress-benchmark > stress-benchmark.log 2>&1
+docker logs fullnode-1 > fullnode-1.log 2>&1     # optional, large
+```
+
+## 6. Run the audit
+
+```bash
+cd <path-to-iota-repo>/dev-tools/iota-private-network/scripts/log-audit
+python3 audit.py /tmp/ds-logs --include-fullnode --json /tmp/ds-audit.json
+```
+
+Exit codes: `0` = PASS (no double-spend leaked), `1` = FAIL (safety violation),
+`2` = INCONCLUSIVE (coverage check `[0]` failed — the parser matched none of a
+signal that must be present, usually because the node log format drifted from
+the parser regexes; nothing was verified, so treat it as not-yet-audited rather
+than safe). Checks: parser coverage, single winner per contested input,
+cross-validator agreement, losers never executed, dropped counts reconcile,
+double-spend pair tracking (and fullnode consistency with `--include-fullnode`).
+`OVERALL: PASS` means no double-spend leaked; on `FAIL` the per-check detail and
+JSON list the offending digests/object refs.
+
+## Cleanup
+
+```bash
+docker rm -f stress-benchmark
+cd <path-to-iota-repo>/dev-tools/grafana-local && docker compose down
+cd <path-to-iota-repo>/dev-tools/iota-private-network && sudo ./cleanup.sh
+```
```

### dev-tools/iota-private-network/scripts/log-audit/audit.py
```diff
@@ -0,0 +1,422 @@
+#!/usr/bin/env python3
+"""Double-spend safety audit for IOTA white-flag conflict resolution.
+
+Usage:
+    python3 audit.py <logs_dir> [--include-fullnode] [--json out.json]
+
+Auto-discovers files in <logs_dir> by name:
+    validator-*.log         → validator parser
+    fullnode-*.log          → fullnode parser (skipped unless --include-fullnode;
+                              large, and only feeds the optional fullnode checks)
+    stress*.log             → stress parser
+
+Exit codes:
+    0 = PASS         — checks ran on real signal and found no safety violation
+    1 = FAIL         — a safety violation (e.g. a loser that also executed);
+                       takes precedence over INCONCLUSIVE
+    2 = INCONCLUSIVE — coverage check failed and no safety violation found: the
+                       parser matched none of a signal that must be present, so
+                       nothing was verified (commonly the node log format
+                       drifted from the parsers)
+"""
+
+from __future__ import annotations
+
+import argparse
+import glob
+import json
+import os
+import sys
+import threading
+import time
+from dataclasses import asdict
+from typing import List
+
+import checks
+import parsers
+
+
+class Watchdog:
+    """Background thread that prints HANG warnings when no progress has been
+    reported for `timeout_s` seconds. Call `tick()` from the producer's
+    progress callback to mark progress.
+    """
+
+    def __init__(self, timeout_s: float, label: str = ""):
+        self.timeout_s = timeout_s
+        self.label = label
+        self.last_tick = time.time()
+        self.stop_event = threading.Event()
+        self.lock = threading.Lock()
+        self.thread = threading.Thread(target=self._run, daemon=True)
+
+    def __enter__(self):
+        self.last_tick = time.time()
+        self.thread.start()
+        return self
+
+    def __exit__(self, *exc):
+        self.stop_event.set()
+
+    def tick(self):
+        with self.lock:
+            self.last_tick = time.time()
+
+    def _run(self):
+        check_interval = max(self.timeout_s / 4.0, 1.0)
+        while not self.stop_event.wait(check_interval):
+            with self.lock:
+                idle = time.time() - self.last_tick
+            if idle > self.timeout_s:
+                print(
+                    f"  !! WATCHDOG: no progress on {self.label} for "
+                    f"{idle:.0f}s — parser may be hung",
+                    flush=True,
+                )
+
+
+def _discover(logs_dir: str):
+    validators = sorted(glob.glob(os.path.join(logs_dir, "validator-*.log")))
+    fullnodes = sorted(glob.glob(os.path.join(logs_dir, "fullnode-*.log")))
+    stress = sorted(glob.glob(os.path.join(logs_dir, "stress*.log")))
+    return validators, fullnodes, stress
+
+
+def _validator_name(path: str) -> str:
+    return os.path.basename(path).removesuffix(".log")
+
+
+def _human(n: int) -> str:
+    if n >= 1_000_000:
+        return f"{n / 1_000_000:.1f}M"
+    if n >= 1_000:
+        return f"{n / 1_000:.1f}k"
+    return str(n)
+
+
+def main() -> int:
+    ap = argparse.ArgumentParser(description=__doc__)
+    ap.add_argument("logs_dir", help="Directory containing the log files")
+    ap.add_argument(
+        "--include-fullnode",
+        action="store_true",
+        help="Parse fullnode-*.log files (large; opt-in)",
+    )
+    ap.add_argument(
+        "--json",
+        dest="json_out",
+        default=None,
+        help="Write machine-readable report to this path",
+    )
+    ap.add_argument(
+        "--watchdog",
+        type=float,
+        default=30.0,
+        help="Seconds without progress before printing a HANG warning",
+    )
+    ap.add_argument(
+        "--max-fullnode-lines",
+        type=int,
+        default=0,
+        help="Stop fullnode parsing after N lines (0 = no limit). For debugging.",
+    )
+    args = ap.parse_args()
+
+    validator_paths, fullnode_paths, stress_paths = _discover(args.logs_dir)
+
+    if not validator_paths:
+        print(f"no validator-*.log files in {args.logs_dir}", file=sys.stderr)
+        return 2
+
+    print(f"=== Double-Spend Conflict Audit ===")
+    print(f"logs dir: {args.logs_dir}")
+    print(f"validators: {len(validator_paths)}")
+    print(f"fullnodes:  {len(fullnode_paths)} "
+          f"({'parsing' if args.include_fullnode else 'skipped (use --include-fullnode)'})")
+    print(f"stress:     {len(stress_paths)}")
+    print()
+
+    # ---- Validator pass --------------------------------------------------
+    validator_events: list = []
+    for path in validator_paths:
+        v = _validator_name(path)
+        t0 = time.time()
+        before = len(validator_events)
+
+        with Watchdog(args.watchdog, label=v) as wd:
+            def _v_progress(line_no, _t0=t0, _v=v, _wd=wd):
+                _wd.tick()
+                rate = line_no / max(time.time() - _t0, 1e-3)
+                print(
+                    f"    {_v}: {_human(line_no)} lines ({_human(int(rate))}/s)",
+                    flush=True,
+                )
+
+            for ev in parsers.parse_validator_log(
+                path, v, progress_cb=_v_progress
+            ):
+                validator_events.append(ev)
+
+        elapsed = time.time() - t0
+        print(
+            f"  {v}: {_human(len(validator_events) - before)} events "
+            f"in {elapsed:.1f}s"
+        )
+
+    # ---- Fullnode pass (optional) ----------------------------------------
+    fn_submissions: set = set()
+    fn_final_failures: dict = {}
+    fn_executed: dict = {}
+
+    if args.include_fullnode and fullnode_paths:
+        for path in fullnode_paths:
+            t0 = time.time()
+            n_sub = n_fail = n_exec = 0
+            name = os.path.basename(path)
+
+            with Watchdog(args.watchdog, label=name) as wd:
+                def _fn_progress(
+                    line_no, ns, nf, ne, _t0=t0, _name=name, _wd=wd
+                ):
+                    _wd.tick()
+                    elapsed = time.time() - _t0
+                    rate = line_no / max(elapsed, 1e-3)
+                    print(
+                        f"    {_name}: {_human(line_no)} lines "
+                        f"({_human(int(rate))}/s, {elapsed:.0f}s elapsed) "
+                        f"sub={_human(ns)} fail={_human(nf)} exec={_human(ne)}",
+                        flush=True,
+                    )
+
+                for ev in parsers.parse_fullnode_log(
+                    path,
+                    progress_cb=_fn_progress,
+                    max_lines=args.max_fullnode_lines,
+                ):
+                    if isinstance(ev, parsers.FnSubmissionSeen):
+                        fn_submissions.add(ev.digest)
+                        n_sub += 1
+                    elif isinstance(ev, parsers.FnFinalFailure):
+                        fn_final_failures[ev.digest] = ev.reason
+                        n_fail += 1
+                    elif isinstance(ev, parsers.FnEffectsExecuted):
+                        fn_executed[ev.digest] = ev.effects_digest
+                        n_exec += 1
+
+            elapsed = time.time() - t0
+            print(
+                f"  {name}: "
+                f"submissions={_human(n_sub)} "
+                f"final_failures={_human(n_fail)} "
+                f"executed={_human(n_exec)} "
+                f"in {elapsed:.1f}s"
+            )
+
+    # ---- Stress pass (optional, informational only) ----------------------
+    stress_gave_up = 0
+    stress_expected_failures = 0
+    double_spend_attempts: list = []
+    # Digests the stress client saw rejected at submission (pre-consensus), so
+    # their absence from validator post-consensus logs is expected (Check F).
+    pre_consensus_rejected: set = set()
+    for path in stress_paths:
+        t0 = time.time()
+        n_attempts = 0
+        n_ds_submits = 0
+        n_gave_up = 0
+        n_expected = 0
+        name = os.path.basename(path)
+
+        with Watchdog(args.watchdog, label=name) as wd:
+            def _s_progress(line_no, _t0=t0, _name=name, _wd=wd):
+                _wd.tick()
+                elapsed = time.time() - _t0
+                rate = line_no / max(elapsed, 1e-3)
+                print(
+                    f"    {_name}: {_human(line_no)} lines "
+                    f"({_human(int(rate))}/s, {elapsed:.0f}s elapsed)",
+                    flush=True,
+                )
+
+            for ev in parsers.parse_stress_log(path, progress_cb=_s_progress):
+                if isinstance(ev, parsers.StressAttempt):
+                    n_attempts += 1
+                    if checks.is_pre_consensus_rejection(ev.err):
+                        pre_consensus_rejected.add(ev.digest)
+                elif isinstance(ev, parsers.StressGaveUp):
+                    n_gave_up += 1
+                elif isinstance(ev, parsers.StressExpectedFailure):
+                    n_expected += 1
+                elif isinstance(ev, parsers.DoubleSpendAttempt):
+                    double_spend_attempts.append(ev)
+                    n_ds_submits += 1
+
+        stress_gave_up += n_gave_up
+        stress_expected_failures += n_expected
+        elapsed = time.time() - t0
+        print(
+            f"  {name}: "
+            f"attempts={_human(n_attempts)} "
+            f"gave_up={n_gave_up} "
+            f"expected_failures={n_expected} "
+            f"double_spend_submits={_human(n_ds_submits)} "
+            f"in {elapsed:.1f}s"
+        )
+
+    print()
+
+    # ---- Run checks ------------------------------------------------------
+    results: List[checks.CheckResult] = []
+    coverage = checks.check_coverage(
+        validator_events,
+        num_validator_logs=len(validator_paths),
+        num_stress_logs=len(stress_paths),
+        num_double_spend_attempts=len(double_spend_attempts),
+        fullnode_enabled=bool(args.include_fullnode and fullnode_paths),
+        num_fn_submissions=len(fn_submissions),
+    )
+    results.append(coverage)
+    results.append(checks.check_single_winner_per_input(validator_events))
+    results.append(checks.check_cross_validator_agreement(validator_events))
+    results.append(checks.check_losers_never_executed(validator_events))
+    results.append(checks.check_batch_counts(validator_events))
+    if args.include_fullnode and fullnode_paths:
+        results.append(
+            checks.check_stress_consistency(
+                validator_events,
+                fn_submissions,
+                fn_final_failures,
+                fn_executed,
+            )
+        )
+    if double_spend_attempts:
+        # The fullnode's terminal-failure reason is a second source of
+        # pre-consensus rejections (e.g. stale input object) when available.
+        for digest, reason in fn_final_failures.items():
+            if checks.is_pre_consensus_rejection(reason):
+                pre_consensus_rejected.add(digest)
+        results.append(
+            checks.check_double_spend_pairs(
+                double_spend_attempts,
+                validator_events,
+                pre_consensus_rejected,
+            )
+        )
+
+    # ---- Render summary --------------------------------------------------
+    print("Check results")
+    print("-------------")
+    for r in results:
+        n_fail = sum(1 for a in r.anomalies if a.severity == "FAIL")
+        n_warn = sum(1 for a in r.anomalies if a.severity == "WARN")
+        if n_fail:
+            status = "FAIL"
+        elif n_warn:
+            status = "WARN"
+        else:
+            status = "PASS"
+        print(
+            f"  [{r.name}] {r.description:<40s} "
+            f"{status} ({_human(r.items_checked)} items, "
+            f"{n_fail} fail / {n_warn} warn)"
+        )
+
+    # A confirmed safety violation in A/B/C/E (FAIL, exit 1) takes precedence
+    # over a coverage failure (INCONCLUSIVE, exit 2): hard evidence of a leak
+    # must surface as FAIL even when the parser also missed some signal.
+    # Coverage failure alone means we verified nothing, so report INCONCLUSIVE
+    # rather than a misleading PASS.
+    coverage_failed = not coverage.passed
+    safety_fail = any(
+        a.severity == "FAIL"
+        for r in results
+        if r is not coverage
+        for a in r.anomalies
+    )
+
+    print()
+    if safety_fail:
+        print("OVERALL: FAIL — anomalies detail below")
+        if coverage_failed:
+            print(
+                "         (parser coverage check [0] also FAILED; a confirmed "
+                "safety violation takes precedence over INCONCLUSIVE)"
+            )
+    elif coverage_failed:
+        print(
+            "OVERALL: INCONCLUSIVE — parser coverage check FAILED; cannot "
+            "certify safety (see check [0] below)"
+        )
+    else:
+        print("OVERALL: PASS — no double-spend leaked")
+        print(
+            "         (proves: exactly one winner per contested input — "
+            "including a two-winners / no-loser leak when winner lines carry "
+            "the acquired object refs — and no loser executed)"
+        )
+
+    print()
+
+    # ---- Detail any anomalies --------------------------------------------
+    any_anomaly = False
+    for r in results:
+        if not r.anomalies:
+            continue
+        any_anomaly = True
+        print(f"-- Check {r.name}: {r.description} ({len(r.anomalies)} anomalies) --")
+        MAX_SHOW = 20
+        for a in r.anomalies[:MAX_SHOW]:
+            print(f"  [{a.severity}] {a.message}")
+            for k, v in a.evidence.items():
+                if isinstance(v, list) and len(v) > 6:
+                    v = v[:6] + [f"... ({len(v)} total)"]
+                print(f"        {k}: {v}")
+        if len(r.anomalies) > MAX_SHOW:
+            print(f"  ... ({len(r.anomalies) - MAX_SHOW} more; see JSON for full list)")
+        print()
+
+    if not any_anomaly:
+        print("(no anomalies)")
+
+    # ---- Machine-readable output -----------------------------------------
+    if args.json_out:
+        json_doc = {
+            "logs_dir": args.logs_dir,
+            "validators": [_validator_name(p) for p in validator_paths],
+            "include_fullnode": args.include_fullnode,
+            "fn_submissions": len(fn_submissions),
+            "fn_final_failures": len(fn_final_failures),
+            "fn_executed": len(fn_executed),
+            "double_spend_submits": len(double_spend_attempts),
+            "overall_status": (
+                "FAIL"
+                if safety_fail
+                else "INCONCLUSIVE"
+                if coverage_failed
+                else "PASS"
+            ),
+            "overall_pass": not (coverage_failed or safety_fail),
+            "checks": [
+                {
+                    "name": r.name,
+                    "description": r.description,
+                    "items_checked": r.items_checked,
+                    "passed": r.passed,
+                    "anomalies": [asdict(a) for a in r.anomalies],
+                }
+                for r in results
+            ],
+        }
+        with open(args.json_out, "w") as f:
+            json.dump(json_doc, f, indent=2, default=str)
+        print(f"\nwrote {args.json_out}")
+
+    if safety_fail:
+        return 1
+    if coverage_failed:
+        return 2
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
```

### dev-tools/iota-private-network/scripts/log-audit/checks.py
```diff
@@ -0,0 +1,668 @@
+"""Invariant checks for double-spend safety verification.
+
+Each check returns a CheckResult listing anomalies (FAIL or WARN). The overall
+audit passes iff no check produces a FAIL.
+"""
+
+from __future__ import annotations
+
+from collections import defaultdict
+from dataclasses import dataclass, field
+from typing import Iterable, List
+
+from parsers import (
+    BatchSummary,
+    DoubleSpendAttempt,
+    Executed,
+    FnEffectsExecuted,
+    FnFinalFailure,
+    FnSubmissionSeen,
+    LoserDropped,
+    StressGaveUp,
+    WinnerLockAcquired,
+)
+
+
+@dataclass
+class Anomaly:
+    severity: str  # "FAIL" or "WARN"
+    message: str
+    evidence: dict = field(default_factory=dict)
+
+
+@dataclass
+class CheckResult:
+    name: str
+    description: str
+    items_checked: int
+    anomalies: List[Anomaly] = field(default_factory=list)
+
+    @property
+    def passed(self) -> bool:
+        return not any(a.severity == "FAIL" for a in self.anomalies)
+
+    @property
+    def warned(self) -> bool:
+        return any(a.severity == "WARN" for a in self.anomalies)
+
+
+# Substrings that identify a transaction rejected BEFORE consensus (at
+# submission), so it never reached the post-consensus owned-object contest and
+# legitimately produces no winner/loser line. Surfaced client-side in the
+# stress log's error and node-side in the fullnode's terminal-failure reason.
+_PRE_CONSENSUS_REJECTION_MARKERS = (
+    "rejected as invalid by more than 1/3 of validator stake during submission",
+    "is not available for consumption, current version",
+)
+
+
+def is_pre_consensus_rejection(reason: str) -> bool:
+    """True if `reason` is a pre-consensus (submission-time) rejection — a tx
+    that never entered a consensus commit, so its absence from validator
+    post-consensus logs is expected, not a completeness gap."""
+    if not reason:
+        return False
+    return any(m in reason for m in _PRE_CONSENSUS_REJECTION_MARKERS)
+
+
+# ---------- Coverage: the parser actually extracted the safety signal ------
+
+def check_coverage(
+    events: Iterable,
+    num_validator_logs: int,
+    num_stress_logs: int,
+    num_double_spend_attempts: int,
+    fullnode_enabled: bool,
+    num_fn_submissions: int,
+) -> CheckResult:
+    """Guard against a vacuous PASS. Every other check derives its FAILs from
+    the *presence* of loser / Executed events; if the parser matched none of
+    them (e.g. the node's log format drifted from the regexes), those checks
+    pass over empty input and the audit would otherwise certify "no
+    double-spend leaked" while having verified nothing.
+
+    This check FAILs when a signal that MUST be present for the double-spend
+    workload is empty, so an empty/stale parse becomes a loud INCONCLUSIVE
+    instead of a silent PASS. A FAIL here means "cannot certify", which the
+    caller maps to a distinct exit code from a genuine safety violation.
+    """
+    n_winners = n_losers = n_executed = 0
+    for ev in events:
+        if isinstance(ev, WinnerLockAcquired):
+            n_winners += 1
+        elif isinstance(ev, LoserDropped):
+            n_losers += 1
+        elif isinstance(ev, Executed):
+            n_executed += 1
+
+    anomalies: List[Anomaly] = []
+    if num_validator_logs > 0:
+        for label, count in (
+            ("winner (passed post-consensus validation)", n_winners),
+            ("loser (conflicts with existing owned-object lock)", n_losers),
+            ("executed (process_transaction succeeded)", n_executed),
+        ):
+            if count == 0:
+                anomalies.append(
+                    Anomaly(
+                        severity="FAIL",
+                        message=(
+                            f"parsed 0 '{label}' events from "
+                            f"{num_validator_logs} validator log(s) — the node "
+                            f"log format may have changed or the workload "
+                            f"exercised no conflicts; cannot certify safety"
+                        ),
+                        evidence={"event": label, "count": count},
+                    )
+                )
+
+    if num_stress_logs > 0 and num_double_spend_attempts == 0:
+        anomalies.append(
+            Anomaly(
+                severity="FAIL",
+                message=(
+                    f"parsed 0 double-spend submission events from "
+                    f"{num_stress_logs} stress log(s) — cannot certify the "
+                    f"workload actually contested any gas coins"
+                ),
+                evidence={"double_spend_attempts": 0},
+            )
+        )
+
+    if fullnode_enabled and num_fn_submissions == 0:
+        anomalies.append(
+            Anomaly(
+                severity="WARN",
+                message=(
+                    "fullnode parsing enabled but 0 submissions observed — "
+                    "fullnode checks (E) ran on empty input (is the fullnode "
+                    "RUST_LOG missing iota_core=debug?)"
+                ),
+                evidence={"fn_submissions": 0},
+            )
+        )
+
+    return CheckResult(
+        name="0",
+        description="Parser coverage (signal present)",
+        items_checked=n_winners + n_losers + n_executed,
+        anomalies=anomalies,
+    )
+
+
+# ---------- A: Per-input single winner ------------------------------------
+
+def check_single_winner_per_input(events: Iterable) -> CheckResult:
+    """For each (object_id, version) input, at most one transaction may be
+    declared the winner across all validators. More than one means different
+    transactions were accepted for the same owned-object version — a true
+    double-spend safety violation.
+
+    Two independent signals feed the per-input winner set:
+      - Winner evidence: a winner logs the object refs it acquired locks on, so
+        two distinct winner digests naming the same (object_id, version) is a
+        direct two-winners / no-loser leak.
+      - Loser evidence: a loser names the tx that out-locked it (`locked_by`),
+        so two distinct `locked_by` for the same input is also a leak.
+
+    Both must agree (a fixed object version has exactly one legitimate winner),
+    so they share one set per input and either source can surface the FAIL.
+    Winner evidence closes the gap that loser evidence alone cannot see — a
+    leak that produces two winners and no loser. It degrades gracefully: winner
+    lines from a node build that logs only the input count contribute no input
+    keys, leaving the loser-based check intact.
+    """
+    input_to_winners: dict = defaultdict(set)
+    input_validators: dict = defaultdict(set)
+    input_losers: dict = defaultdict(set)
+
+    for ev in events:
+        if isinstance(ev, WinnerLockAcquired):
+            for key in ev.inputs:
+                input_to_winners[key].add(ev.digest)
+                input_validators[key].add(ev.validator)
+        elif isinstance(ev, LoserDropped):
+            key = (ev.obj_id, ev.obj_version)
+            input_to_winners[key].add(ev.locked_by)
+            input_validators[key].add(ev.validator)
+            input_losers[key].add(ev.digest)
+
+    anomalies: List[Anomaly] = []
+    for inp, winners in input_to_winners.items():
+        if len(winners) > 1:
+            anomalies.append(
+                Anomaly(
+                    severity="FAIL",
+                    message=(
+                        f"Input {inp[0]}@v{inp[1]} has {len(winners)} "
+                        f"distinct declared winners — double-spend leaked"
+                    ),
+                    evidence={
+                        "object_id": inp[0],
+                        "version": inp[1],
+                        "winners": sorted(winners),
+                        "losers": sorted(input_losers[inp]),
+                        "validators_reporting": sorted(input_validators[inp]),
+                    },
+                )
+            )
+
+    return CheckResult(
+        name="A",
+        description="Per-input single winner",
+        items_checked=len(input_to_winners),
+        anomalies=anomalies,
+    )
+
+
+# ---------- B: Cross-validator agreement ----------------------------------
+
+def check_cross_validator_agreement(events: Iterable) -> CheckResult:
+    """For each tx digest, every validator that observed it must reach the
+    same verdict (winner or loser). Disagreement implies non-deterministic
+    conflict resolution.
+    """
+    # digest -> validator -> verdict ("winner" | "loser")
+    verdicts: dict = defaultdict(dict)
+    locked_by_seen: dict = defaultdict(lambda: defaultdict(set))
+
+    for ev in events:
+        if isinstance(ev, WinnerLockAcquired):
+            verdicts[ev.digest][ev.validator] = "winner"
+        elif isinstance(ev, LoserDropped):
+            verdicts[ev.digest][ev.validator] = "loser"
+            locked_by_seen[ev.digest][ev.validator].add(ev.locked_by)
+
+    anomalies: List[Anomaly] = []
+    for digest, per_validator in verdicts.items():
+        verdict_set = set(per_validator.values())
+        # Treat all loser-* variants as equivalent for safety purposes: a tx
+        # that was rejected on one validator and accepted on another is the bug.
+        normalised = {("winner" if v == "winner" else "loser") for v in verdict_set}
+        if len(normalised) > 1:
+            anomalies.append(
+                Anomaly(
+                    severity="FAIL",
+                    message=f"Validators disagree on tx {digest}",
+                    evidence={
+                        "digest": digest,
+                        "verdicts": per_validator,
+                    },
+                )
+            )
+
+        # Validators reporting locked_by for the same loser must agree on the
+        # winner; disagreement is a real safety failure, hence FAIL.
+        all_winners = set()
+        for vset in locked_by_seen.get(digest, {}).values():
+            all_winners.update(vset)
+        if len(all_winners) > 1:
+            anomalies.append(
+                Anomaly(
+                    severity="FAIL",
+                    message=(
+                        f"Validators disagree on which tx won against loser "
+                        f"{digest}"
+                    ),
+                    evidence={
+                        "loser_digest": digest,
+                        "locked_by_per_validator": {
+                            v: sorted(s)
+                            for v, s in locked_by_seen[digest].items()
+                        },
+                    },
+                )
+            )
+
+    return CheckResult(
+        name="B",
+        description="Cross-validator agreement",
+        items_checked=len(verdicts),
+        anomalies=anomalies,
+    )
+
+
+# ---------- C: Executions match winners -----------------------------------
+
+def check_losers_never_executed(events: Iterable) -> CheckResult:
+    """A transaction recorded as a loser (any conflict variant) on a given
+    validator must NEVER appear as Executed on that same validator. This is
+    the headline safety invariant: a rejected tx that executes anyway is a
+    direct double-spend.
+
+    The complementary direction (every winner executes) is intentionally not
+    checked — non-conflict-validated transactions (genesis, system) also
+    emit `process_transaction succeeded`, so a missing winner is normal.
+    """
+    losers: dict = {}  # (validator, digest) -> True
+    exec_fx: dict = {}  # (validator, digest) -> fx_digest
+
+    for ev in events:
+        if isinstance(ev, LoserDropped):
+            losers[(ev.validator, ev.digest)] = True
+        elif isinstance(ev, Executed):
+            exec_fx[(ev.validator, ev.digest)] = ev.fx_digest
+
+    anomalies: List[Anomaly] = []
+    for vd in losers:
+        if vd in exec_fx:
+            anomalies.append(
+                Anomaly(
+                    severity="FAIL",
+                    message=(
+                        f"Tx {vd[1]} rejected as loser on {vd[0]} but "
+                        f"ALSO executed on {vd[0]} — double-spend leaked"
+                    ),
+                    evidence={
+                        "validator": vd[0],
+                        "digest": vd[1],
+                        "fx_digest": exec_fx[vd],
+                    },
+                )
+            )
+
+    return CheckResult(
+        name="C",
+        description="Losers never executed",
+        items_checked=len(losers),
+        anomalies=anomalies,
+    )
+
+
+# ---------- D: Batch counts reconcile -------------------------------------
+
+def check_batch_counts(events: Iterable) -> CheckResult:
+    """For each validator, the total `num_dropped` across BatchSummary lines
+    should be >= the count of individual LoserDropped events. `num_dropped`
+    counts ALL post-consensus drops (owned-object lock conflicts plus
+    validity-check, deny-check and input-extraction failures), whereas
+    LoserDropped counts only the lock conflicts, so a small positive
+    `dropped - losers` gap is expected. A negative gap (more loser lines than
+    drops) or a large positive gap suggests the parser is missing loser lines.
+    This is diagnostic only (WARN); it never fails the audit.
+
+    We do NOT compare winners vs `num_retained`: the summary log only fires
+    when `num_dropped > 0`, so its retained field only covers contentious
+    commits and would underreport against the total Winner-event count.
+    """
+    per_v_loser = defaultdict(int)
+    per_v_sum_dropped = defaultdict(int)
+
+    for ev in events:
+        if isinstance(ev, LoserDropped):
+            per_v_loser[ev.validator] += 1
+        elif isinstance(ev, BatchSummary):
+            per_v_sum_dropped[ev.validator] += ev.num_dropped
+
+    anomalies: List[Anomaly] = []
+    validators = set(per_v_loser) | set(per_v_sum_dropped)
+    for v in sorted(validators):
+        l = per_v_loser.get(v, 0)
+        d = per_v_sum_dropped.get(v, 0)
+        if l != d:
+            anomalies.append(
+                Anomaly(
+                    severity="WARN",
+                    message=(
+                        f"{v}: loser events={l} vs sum(dropped)={d} "
+                        f"(diff {l - d:+d})"
+                    ),
+                    evidence={
+                        "validator": v,
+                        "loser_events": l,
+                        "dropped_total": d,
+                    },
+                )
+            )
+
+    return CheckResult(
+        name="D",
+        description="Dropped counts reconcile",
+        items_checked=len(validators),
+        anomalies=anomalies,
+    )
+
+
+# ---------- E: Stress / fullnode / validator consistency ------------------
+
+def check_stress_consistency(
+    validator_events: Iterable,
+    fn_submissions: set,
+    fn_final_failures: dict,
+    fn_executed: dict,
+) -> CheckResult:
+    """Cross-check the fullnode's view (which transactions were submitted and
+    what their terminal outcomes were) against the validator-side verdicts.
+
+    Anomaly classes:
+      - A digest that finalised on the fullnode (effects observed) but every
+        validator recorded it as a loser → finality-reporting bug.
+      - A digest that the fullnode declared as a final failure but at least
+        one validator says it won → finality-reporting bug (opposite direction).
+      - A digest submitted by the fullnode but never observed on any
+        validator → completeness gap, not safety. Reported as WARN.
+    """
+    winners_any: set = set()
+    losers_any: set = set()
+    for ev in validator_events:
+        if isinstance(ev, WinnerLockAcquired):
+            winners_any.add(ev.digest)
+        elif isinstance(ev, LoserDropped):
+            losers_any.add(ev.digest)
+
+    anomalies: List[Anomaly] = []
+
+    for digest in fn_executed:
+        if digest in losers_any and digest not in winners_any:
+            anomalies.append(
+                Anomaly(
+                    severity="FAIL",
+                    message=(
+                        f"Tx {digest} reported Executed by fullnode but "
+                        f"recorded only as loser on validators"
+                    ),
+                    evidence={
+                        "digest": digest,
+                        "fn_effects_digest": fn_executed[digest],
+                    },
+                )
+            )
+
+    for digest, reason in fn_final_failures.items():
+        if digest in winners_any:
+            anomalies.append(
+                Anomaly(
+                    severity="FAIL",
+                    message=(
+                        f"Tx {digest} reported failed by fullnode but won on "
+                        f"at least one validator"
+                    ),
+                    evidence={
+                        "digest": digest,
+                        "fn_reason": reason,
+                    },
+                )
+            )
+
+    missing_on_validators = fn_submissions - (winners_any | losers_any)
+    if missing_on_validators:
+        # Bucket by what the fullnode said happened to them.
+        bucket_stale_object = []
+        bucket_other_failure = []
+        bucket_no_outcome = []
+        for d in missing_on_validators:
+            reason = fn_final_failures.get(d)
+            if reason is None:
+                bucket_no_outcome.append(d)
+            elif "is not available for consumption, current version" in reason:
+                bucket_stale_object.append(d)
+            else:
+                bucket_other_failure.append(d)
+
+        # Pre-consensus stale-object rejections are benign — a separate safety
+        # layer caught them before they reached consensus. Report informationally.
+        if bucket_stale_object:
+            anomalies.append(
+                Anomaly(
+                    severity="WARN",
+                    message=(
+                        f"{len(bucket_stale_object)} submitted txs rejected "
+                        f"pre-consensus (stale input object) — benign, "
+                        f"pre-consensus safety layer caught them"
+                    ),
+                    evidence={
+                        "count": len(bucket_stale_object),
+                        "sample": sorted(bucket_stale_object)[:10],
+                    },
+                )
+            )
+
+        # Other terminal failures need closer inspection.
+        if bucket_other_failure:
+            anomalies.append(
+                Anomaly(
+                    severity="WARN",
+                    message=(
+                        f"{len(bucket_other_failure)} submitted txs failed "
+                        f"on fullnode for non-stale reasons and never reached "
+                        f"validator post-consensus"
+                    ),
+                    evidence={
+                        "count": len(bucket_other_failure),
+                        "sample": sorted(bucket_other_failure)[:10],
+                    },
+                )
+            )
+
+        # No terminal outcome at all is the most suspicious — could be a
+        # truncated log or a genuine completeness gap.
+        if bucket_no_outcome:
+            anomalies.append(
+                Anomaly(
+                    severity="WARN",
+                    message=(
+                        f"{len(bucket_no_outcome)} submitted txs have no "
+                        f"recorded terminal outcome on fullnode AND no "
+                        f"validator post-consensus event — possible log "
+                        f"truncation or pipeline gap"
+                    ),
+                    evidence={
+                        "count": len(bucket_no_outcome),
+                        "sample": sorted(bucket_no_outcome)[:10],
+                    },
+                )
+            )
+
+    return CheckResult(
+        name="E",
+        description="Fullnode / validator consistency",
+        items_checked=len(fn_submissions),
+        anomalies=anomalies,
+    )
+
+
+# ---------- F: Double-spend pair tracking ---------------------------------
+
+def check_double_spend_pairs(
+    double_spend_attempts: Iterable,
+    validator_events: Iterable,
+    pre_consensus_rejected: set = frozenset(),
+) -> CheckResult:
+    """Cross-reference the double-spend workload's pre-submission log against
+    validator verdicts.
+
+    The workload emits one `DoubleSpendAttempt(pair_id, gas_object,
+    gas_version, digest, sink, ts)` per submitted tx. Attempts that share a
+    `pair_id` contest the same gas coin and are *expected* to collide on the
+    validator side. This check groups attempts by pair and, for each pair,
+    reports how many submitted digests were observed by at least one validator
+    and how the validator quorum split them between winner / loser / executed.
+
+    A submitted digest that no validator observed is only a concern if it
+    cannot be explained: the workload submits faster than the contested coin
+    advances, so many attempts reference an already-consumed gas version and
+    are rejected pre-consensus (stale object) before reaching the
+    owned-object contest. `pre_consensus_rejected` carries the digests known
+    (from the stress error and/or fullnode terminal failure) to have been
+    rejected at submission; those are accounted for as benign and only the
+    unexplained remainder is flagged.
+
+    Anomaly classes:
+      - WARN: a pair has missing digests NOT explained by a pre-consensus
+              rejection (a genuine completeness gap).
+      - WARN: a pair has zero winners despite having multiple attempts
+              (the contest never produced a winning tx on any validator).
+      - INFO: total missing digests accounted for as pre-consensus rejections.
+    """
+    # pair_id -> list of attempts (preserve order for diagnostics)
+    by_pair: dict = defaultdict(list)
+    # Track first-seen attempt per digest to keep evidence compact.
+    digest_to_attempt: dict = {}
+    for ev in double_spend_attempts:
+        by_pair[ev.pair_id].append(ev)
+        digest_to_attempt.setdefault(ev.digest, ev)
+
+    # Validator-side digest sets (built once).
+    winners_any: set = set()
+    losers_any: set = set()
+    executed_any: set = set()
+    for ev in validator_events:
+        if isinstance(ev, WinnerLockAcquired):
+            winners_any.add(ev.digest)
+        elif isinstance(ev, LoserDropped):
+            losers_any.add(ev.digest)
+        elif isinstance(ev, Executed):
+            executed_any.add(ev.digest)
+
+    seen_on_validator = winners_any | losers_any
+
+    anomalies: List[Anomaly] = []
+    total_missing = 0
+    total_accounted = 0
+    for pair_id in sorted(by_pair):
+        attempts = by_pair[pair_id]
+        unique_digests = {a.digest for a in attempts}
+        gas_objects = {a.gas_object for a in attempts}
+        winners = unique_digests & winners_any
+        losers = unique_digests & losers_any
+        executed = unique_digests & executed_any
+        missing = unique_digests - seen_on_validator
+        accounted = missing & pre_consensus_rejected
+        unexplained = missing - pre_consensus_rejected
+        total_missing += len(missing)
+        total_accounted += len(accounted)
+
+        if unexplained:
+            # Show a small sample with their (gas_object, gas_version) so the
+            # user can find the matching lines in the stress log.
+            sample = sorted(unexplained)[:6]
+            sample_detail = [
+                {
+                    "tx_digest": d,
+                    "gas_object": digest_to_attempt[d].gas_object,
+                    "gas_version": digest_to_attempt[d].gas_version,
+                }
+                for d in sample
+            ]
+            anomalies.append(
+                Anomaly(
+                    severity="WARN",
+                    message=(
+                        f"pair {pair_id}: {len(unexplained)}/"
+                        f"{len(unique_digests)} submitted digests never "
+                        f"observed on any validator and not explained by a "
+                        f"pre-consensus rejection"
+                    ),
+                    evidence={
+                        "pair_id": pair_id,
+                        "gas_objects": sorted(gas_objects),
+                        "submitted_unique": len(unique_digests),
+                        "missing_count": len(missing),
+                        "accounted_pre_consensus": len(accounted),
+                        "unexplained_count": len(unexplained),
+                        "unexplained_sample": sample_detail,
+                    },
+                )
+            )
+
+        if len(unique_digests) >= 2 and not winners:
+            anomalies.append(
+                Anomaly(
+                    severity="WARN",
+                    message=(
+                        f"pair {pair_id}: {len(unique_digests)} distinct "
+                        f"digests submitted but no winner recorded on any "
+                        f"validator"
+                    ),
+                    evidence={
+                        "pair_id": pair_id,
+                        "gas_objects": sorted(gas_objects),
+                        "submitted_unique": len(unique_digests),
+                        "losers_count": len(losers),
+                        "executed_count": len(executed),
+                    },
+                )
+            )
+
+    if total_accounted:
+        anomalies.append(
+            Anomaly(
+                severity="INFO",
+                message=(
+                    f"{total_accounted}/{total_missing} digests missing from "
+                    f"validator post-consensus logs accounted for as "
+                    f"pre-consensus rejections (stale gas object) — benign"
+                ),
+                evidence={
+                    "accounted_pre_consensus": total_accounted,
+                    "total_missing": total_missing,
+                },
+            )
+        )
+
+    return CheckResult(
+        name="F",
+        description="Double-spend pair tracking",
+        items_checked=len(by_pair),
+        anomalies=anomalies,
+    )
```

### dev-tools/iota-private-network/scripts/log-audit/parsers.py
```diff
@@ -0,0 +1,353 @@
+"""Parsers for IOTA validator, fullnode, and stress-benchmark logs.
+
+Each parser is a generator yielding typed event namedtuples. Lines are pre-filtered
+by cheap substring tests before regex application to keep the cost flat on multi-
+gigabyte logs.
+"""
+
+from __future__ import annotations
+
+import re
+from collections import namedtuple
+from typing import Iterator, Optional
+
+# ---------- Event types ---------------------------------------------------
+
+# Validator events
+# `inputs` is the list of (obj_id, obj_version) the winner acquired locks on,
+# parsed from the winner line's `owned_inputs` field. It is empty for node
+# builds that log only the count, in which case winner-side single-winner
+# detection (Check A) degrades gracefully to loser evidence alone.
+WinnerLockAcquired = namedtuple(
+    "WinnerLockAcquired", "validator digest num_inputs inputs ts"
+)
+# A transaction dropped post-consensus because one of its owned inputs was
+# already locked by an earlier transaction. The node resolves all three lock
+# tiers (same-commit / consensus-quarantine / persistent DB) through a single
+# `find_existing_lock` path and emits one unified line, so the audit models the
+# loser with a single event type. `locked_by` is the digest of the winning tx
+# that holds the lock on `(obj_id, obj_version)`.
+LoserDropped = namedtuple(
+    "LoserDropped",
+    "validator digest obj_id obj_version obj_digest locked_by ts",
+)
+BatchSummary = namedtuple(
+    "BatchSummary", "validator num_dropped num_retained ts"
+)
+Executed = namedtuple("Executed", "validator digest fx_digest ts")
+
+# Fullnode events
+FnSubmissionSeen = namedtuple("FnSubmissionSeen", "digest ts")
+FnFinalFailure = namedtuple("FnFinalFailure", "digest reason ts")
+FnEffectsExecuted = namedtuple(
+    "FnEffectsExecuted", "digest effects_digest validator ts"
+)
+
+# Stress events
+StressAttempt = namedtuple("StressAttempt", "digest retry_cnt err ts")
+StressGaveUp = namedtuple("StressGaveUp", "digest attempts ts")
+StressExpectedFailure = namedtuple("StressExpectedFailure", "ts")
+# Emitted by the double-spend workload right before each tx is submitted.
+# `pair_id` identifies the conflict group: all attempts with the same pair_id
+# contest the same gas coin and are expected to collide.
+DoubleSpendAttempt = namedtuple(
+    "DoubleSpendAttempt", "pair_id gas_object gas_version digest sink ts"
+)
+
+
+# ---------- Common patterns -----------------------------------------------
+
+# Each line starts with the app's RFC3339 timestamp as the first token.
+_TS_RE = re.compile(r"^(\S+)\s+")
+
+# Validator-side regexes
+_RE_WINNER = re.compile(
+    r'Transaction passed post-consensus validation, acquired all object locks '
+    r'digest=Digest\("([^"]+)"\) num_owned_inputs=(\d+)'
+)
+# One (object_id, version) per owned input, as rendered inside the winner
+# line's `owned_inputs` list (same ObjectReference shape as the loser line's
+# obj_ref). `findall` collects every ref the winner locked.
+_RE_OWNED_REF = re.compile(
+    r'object_id: ObjectId\("([^"]+)"\), version: Version\((\d+)\)'
+)
+_RE_LOSER = re.compile(
+    r'Transaction conflicts with existing owned-object lock, dropping '
+    r'digest=Digest\("([^"]+)"\) obj_ref=ObjectReference \{ '
+    r'object_id: ObjectId\("([^"]+)"\), version: Version\((\d+)\), '
+    r'digest: Digest\("([^"]+)"\) \} locked_by=Digest\("([^"]+)"\)'
+)
+_RE_BATCH = re.compile(
+    r'Post-consensus validation dropped transactions '
+    r'num_dropped=(\d+) num_retained=(\d+)'
+)
+_RE_EXEC = re.compile(
+    r'process_transaction succeeded tx_digest=Digest\("([^"]+)"\) '
+    r'fx_digest=Digest\("([^"]+)"\)'
+)
+
+# Fullnode-side regexes
+_RE_FN_SPAN_DIGEST = re.compile(
+    r'drive_transaction\{tx_digest=Some\(Digest\("([^"]+)"\)\)'
+)
+_RE_FN_FINAL_FAIL = re.compile(
+    r'User transaction (?:failed to finalize|timed out) .*?: (.+?)$'
+)
+_RE_FN_EXEC_RETURN = re.compile(
+    r'effects_certifier: return=\[\(Digest\("([^"]+)"\), '
+    r'Executed \{ effects_digest: Digest\("([^"]+)"\)'
+)
+_RE_FN_VALIDATOR = re.compile(r'validator_display_name="([^"]+)"')
+
+# Stress-side regexes
+_RE_STRESS_RETRY = re.compile(
+    r'Transaction failed with err: (.*?) '
+    r'tx_digest=Digest\("([^"]+)"\) retry_cnt=(\d+)'
+)
+_RE_STRESS_GAVE_UP = re.compile(
+    r'Transaction execution got error: Transaction Digest\("([^"]+)"\) '
+    r'failed for (\d+) times'
+)
+_RE_DOUBLE_SPEND_SUBMIT = re.compile(
+    r'pair_id=(\d+) '
+    r'gas_object=ObjectId\("([^"]+)"\) '
+    r'gas_version=Version\((\d+)\) '
+    r'tx_digest=Digest\("([^"]+)"\)'
+    r'(?: sink=(\S+))?'
+)
+
+
+# ---------- Helpers -------------------------------------------------------
+
+def _app_ts(line: str) -> Optional[str]:
+    m = _TS_RE.match(line)
+    return m.group(1) if m else None
+
+
+def _app_ts_fast(line: str) -> Optional[str]:
+    """Pure-string variant of _app_ts — avoids regex overhead in hot paths.
+    Returns the first whitespace-separated token (the app's RFC3339 timestamp).
+    Logs collected via `docker logs` without `-t` begin directly with the app
+    timestamp; with `-t` the leading docker timestamp is itself valid, so the
+    first token is correct either way."""
+    space1 = line.find(" ")
+    if space1 == -1:
+        return None
+    return line[:space1]
+
+
+# ---------- Validator parser ----------------------------------------------
+
+def parse_validator_log(
+    path: str,
+    validator: str,
+    progress_cb=None,
+    progress_every: int = 500_000,
+) -> Iterator[tuple]:
+    with open(path, "r", errors="replace") as f:
+        for line_no, line in enumerate(f, 1):
+            if progress_cb is not None and line_no % progress_every == 0:
+                progress_cb(line_no)
+
+            # Cheap pre-filter — vast majority of lines drop out here.
+            if (
+                "post_consensus_validation" not in line
+                and "process_transaction succeeded" not in line
+            ):
+                continue
+
+            ts = _app_ts_fast(line)
+            if ts is None:
+                continue
+
+            if "passed post-consensus validation" in line:
+                m = _RE_WINNER.search(line)
+                if m:
+                    inputs = [
+                        (oid, int(ver))
+                        for oid, ver in _RE_OWNED_REF.findall(line)
+                    ]
+                    yield WinnerLockAcquired(
+                        validator, m.group(1), int(m.group(2)), inputs, ts
+                    )
+                continue
+
+            if "conflicts with existing owned-object lock" in line:
+                m = _RE_LOSER.search(line)
+                if m:
+                    yield LoserDropped(
+                        validator,
+                        m.group(1),
+                        m.group(2),
+                        int(m.group(3)),
+                        m.group(4),
+                        m.group(5),
+                        ts,
+                    )
+                continue
+
+            if "Post-consensus validation dropped" in line:
+                m = _RE_BATCH.search(line)
+                if m:
+                    yield BatchSummary(
+                        validator, int(m.group(1)), int(m.group(2)), ts
+                    )
+                continue
+
+            if "process_transaction succeeded" in line:
+                m = _RE_EXEC.search(line)
+                if m:
+                    yield Executed(validator, m.group(1), m.group(2), ts)
+                continue
+
+
+# ---------- Fullnode parser -----------------------------------------------
+
+_FN_DIGEST_PREFIX = 'drive_transaction{tx_digest=Some(Digest("'
+_FN_DIGEST_PREFIX_LEN = len(_FN_DIGEST_PREFIX)
+
+
+def parse_fullnode_log(
+    path: str,
+    progress_cb=None,
+    progress_every: int = 250_000,
+    max_lines: int = 0,
+) -> Iterator[tuple]:
+    """Yields submission-related events. Most lines are repeated span context;
+    we only emit:
+      - FnSubmissionSeen on first occurrence of a digest in any drive_transaction span
+      - FnFinalFailure   on terminal "User transaction failed/timed out" lines
+      - FnEffectsExecuted on effects_certifier return=[(Digest, Executed {...})]
+
+    Hot path uses pure string ops (find/substring) rather than regex; regex
+    only fires on the rare lines that match a terminal-event substring.
+
+    Assumption: every line of interest carries the `drive_transaction{tx_digest=
+    Some(Digest("..."))}` span — the digest is extracted from it first and the
+    line is skipped outright if absent. This holds because the terminal-failure
+    and effects-return logs are emitted inside that span, but it means a failure
+    or execution line that ever loses the span would be silently dropped (the
+    coverage check guards only against *zero* fullnode submissions, not a
+    partial miss).
+
+    progress_cb(line_no, n_submissions, n_failures, n_executed) is called every
+    `progress_every` lines for monitoring long runs.
+    """
+    seen_digests: set = set()
+    n_sub = n_fail = n_exec = 0
+    line_no = 0  # bound for the final progress tick even if the file is empty
+
+    with open(path, "r", errors="replace") as f:
+        for line_no, line in enumerate(f, 1):
+            if progress_cb is not None and line_no % progress_every == 0:
+                progress_cb(line_no, n_sub, n_fail, n_exec)
+            if max_lines and line_no >= max_lines:
+                break
+
+            # Locate the digest substring directly without regex.
+            pos = line.find(_FN_DIGEST_PREFIX)
+            if pos == -1:
+                continue
+            start = pos + _FN_DIGEST_PREFIX_LEN
+            end = line.find('"', start)
+            if end == -1:
+                continue
+            digest = line[start:end]
+
+            ts = _app_ts_fast(line)
+            if ts is None:
+                continue
+
+            # First-sight tracking.
+            if digest not in seen_digests:
+                seen_digests.add(digest)
+                n_sub += 1
+                yield FnSubmissionSeen(digest, ts)
+
+            # Terminal failure — only the top-level drive_transaction INFO log.
+            # Cheap substring gate first; regex only on candidates.
+            # "Retrying ..." marks the retriable per-attempt log (not terminal):
+            # the tx may still go on to win, so counting it as a final failure
+            # produces spurious cross-validator disagreement (see Check E).
+            if "User transaction" in line and (
+                "failed to finalize" in line or "timed out" in line
+            ):
+                if (
+                    "submit_transaction" not in line
+                    and "drive_transaction_once" not in line
+                    and "Retrying" not in line
+                ):
+                    fm = _RE_FN_FINAL_FAIL.search(line)
+                    reason = fm.group(1).strip() if fm else line.strip()
+                    n_fail += 1
+                    yield FnFinalFailure(digest, reason, ts)
+                continue
+
+            # Execution effects returned from a validator.
+            if "effects_certifier: return=" in line and "Executed {" in line:
+                em = _RE_FN_EXEC_RETURN.search(line)
+                if em:
+                    vm = _RE_FN_VALIDATOR.search(line)
+                    n_exec += 1
+                    yield FnEffectsExecuted(
+                        em.group(1),
+                        em.group(2),
+                        vm.group(1) if vm else "?",
+                        ts,
+                    )
+
+    # Final progress tick.
+    if progress_cb is not None:
+        progress_cb(line_no, n_sub, n_fail, n_exec)
+
+
+# ---------- Stress parser -------------------------------------------------
+
+def parse_stress_log(
+    path: str,
+    progress_cb=None,
+    progress_every: int = 500_000,
+) -> Iterator[tuple]:
+    with open(path, "r", errors="replace") as f:
+        for line_no, line in enumerate(f, 1):
+            if progress_cb is not None and line_no % progress_every == 0:
+                progress_cb(line_no)
+
+            # Lines from the double-spend workload use target=double_spend,
+            # so the `iota_benchmark` substring is absent. Accept either.
+            if "iota_benchmark" not in line and "double_spend" not in line:
+                continue
+            ts = _app_ts_fast(line)
+            if ts is None:
+                continue
+
+            if "Transaction failed with err:" in line:
+                m = _RE_STRESS_RETRY.search(line)
+                if m:
+                    yield StressAttempt(
+                        m.group(2), int(m.group(3)), m.group(1), ts
+                    )
+                continue
+
+            if "Transaction execution got error:" in line:
+                m = _RE_STRESS_GAVE_UP.search(line)
+                if m:
+                    yield StressGaveUp(m.group(1), int(m.group(2)), ts)
+                continue
+
+            if "Transaction failed with expected failure type" in line:
+                yield StressExpectedFailure(ts)
+                continue
+
+            if "submitting double-spend tx" in line:
+                m = _RE_DOUBLE_SPEND_SUBMIT.search(line)
+                if m:
+                    yield DoubleSpendAttempt(
+                        int(m.group(1)),
+                        m.group(2),
+                        int(m.group(3)),
+                        m.group(4),
+                        m.group(5) or "",
+                        ts,
+                    )
+                continue
```
