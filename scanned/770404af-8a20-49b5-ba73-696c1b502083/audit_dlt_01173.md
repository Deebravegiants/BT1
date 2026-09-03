# [?] Fix oob memory access in NibbleExtensions in certain scenarios (#10276)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-03
Source: https://github.com/NethermindEth/nethermind/commit/5599295526600b0b58b0539c4f5135b2b026c692
Type: security-commit

## Details
Fix oob memory access in NibbleExtensions in certain scenarios (#10276)

* Initial plan

* Gate intrinsic usage in benchmarks and document Blake2 methods

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Add Debug.Assert guard to Avx2Reverse256InPlace method

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Address code review: use exceptions instead of Debug.Assert for runtime safety

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Make Avx2Reverse256InPlace internal with Debug.Assert instead of runtime exceptions

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Fix NibbleExtensions Vector256.Shuffle to require AVX2 on x86 (fixes N5095 crash)

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Revert "Fix NibbleExtensions Vector256.Shuffle" - analysis was incorrect

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Fix critical out-of-bounds bug in NibbleExtensions causing v1.36.0 crashes

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Add comprehensive tests for BytesToNibbleBytes to detect out-of-bounds bugs

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Remove unnecessary offset on line 52 - processed is always 0 there


_Trimmed to 38 lines — full report: https://github.com/NethermindEth/nethermind/commit/5599295526600b0b58b0539c4f5135b2b026c692_
