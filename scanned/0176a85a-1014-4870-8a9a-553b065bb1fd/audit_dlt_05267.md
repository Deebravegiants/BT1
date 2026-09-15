# [?] eth/protocols: pre-decode item count validation (CVE-2026-26313 mitigation)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2026-03-27
Source: https://github.com/etclabscore/core-geth/commit/7940b28167825389fd510f97e5e29c7eb6ed770c
Type: security-commit

## Details
eth/protocols: pre-decode item count validation (CVE-2026-26313 mitigation)

Add item count validation before full RLP message decoding in both eth
and snap protocol handlers. This prevents memory amplification attacks
where compact RLP-encoded items expand into large in-memory objects.

The check uses rlp.CountValues on the raw payload to count items
without allocating memory for decoded objects. Messages exceeding the
expected limits are rejected before any decoding occurs.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
