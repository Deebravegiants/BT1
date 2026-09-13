# [M] sqlparse: Reindentation of tuple lists causes near-cap quadratic CPU consumption

## Summary
Severity: Medium
Advisory: GHSA-cfqr-cjx5-5jcm
CVE: CVE-2026-84305
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-cfqr-cjx5-5jcm
Type: github-advisory

## Affected
- PyPI: `sqlparse` — affected >=0 <0.6.0

## Details
### Summary

When SQL is formatted with reindentation enabled, `ReindentFilter` repeatedly rebuilds prefixes of the current statement to calculate token offsets. An attacker who controls SQL sent to this opt-in formatting path can supply a parenthesized tuple list that remains just below the grouping-token cap. Thousands of offset calculations then traverse an expanding token tree, causing multi-second CPU consumption from an input of roughly 16 KB and degrading service availability.

### Details

`ReindentFilter._get_offset()` joins the tokens returned by `_flatten_up_to_token()` to calculate the current output position. Each call begins by flattening the current statement from its start and walks until the target token. Tuple-list reindentation invokes this calculation repeatedly as it processes many parenthesized values, so later calls redo an increasingly large amount of prior work.

The vulnerable path is reached through `sqlparse.format(sql, reindent=True)` and `sqlformat --reindent`. A carefully sized tuple list completes grouping below the configured token cap and then enters the expensive reindentation path; a slightly larger input may instead be rejected quickly by the cap.

Relevant code locations:

- `sqlparse/formatter.py:170` — enabling `ReindentFilter`
- `sqlparse/filters/reindent.py:30` — repeated flattening from the statement start
- `sqlparse/filters/reindent.py:44` — prefix joining for offset calculation
- `sqlparse/filters/reindent.py:216` — tuple-list processing path

### PoC

A complete validated reproduction is attached as [reindent_tuple_list_cpu_dos-poc.zip](https://github.com/user-attachments/files/29410152/reindent_tuple_list_cpu_dos-poc.zip). The archive contains `reproduction/` at its root, uses Git and Docker, and compares two same-shape tuple-list inputs formatted with reindentation enabled.

Extract the archive beside this report, then run:

```console
./reproduction/run.sh
```

Observed result:

The 600-tuple baseline completed in 0.649 seconds, while the below-cap 1,425-tuple input completed in 4.999 seconds. The run emitted `EVOHUNT_REINDENT_DOS_VERIFIED` and completed successfully.

Verification method:

The verification helper formats two same-shape tuple-list payloads with `reindent=True` and fails unless the larger payload completes successfully, takes at least 2.0 seconds, and takes at least 4x the baseline.

Limitations:

No reproduction blocker was recorded. Timing varies by host, and exploitation requires the reindentation option or corresponding CLI mode to be enabled.

### Impact

This is a CPU resource-exhaustion vulnerability in workflows that reindent attacker-controlled SQL. A small crafted tuple-list input can occupy a worker for several seconds, enabling request delays, reduced throughput, or worker starvation when payloads are processed repeatedly or concurrently.

The affected reindentation behavior is opt-in, and sqlparse itself does not provide network exposure; reachability depends on the consuming application or CLI workflow. The demonstrated effect is CPU consumption in a single formatting call, not process termination, code execution, or confidentiality or integrity impact.

## References
- https://github.com/andialbrecht/sqlparse/security/advisories/GHSA-cfqr-cjx5-5jcm
- https://github.com/andialbrecht/sqlparse/commit/a51df6d9e2d31b44be9adb6bc8732517db6bf96b
- https://github.com/andialbrecht/sqlparse
- https://github.com/andialbrecht/sqlparse/releases/tag/0.6.0
