# [?] fix: reject blocks whose packed gas-limit sum overflows U256

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-27
Source: https://github.com/Conflux-Chain/conflux-rust/commit/86530fa476ad04ad3fccd3b50e56f247d679496c
Type: security-commit

## Details
fix: reject blocks whose packed gas-limit sum overflows U256

verify_sync_graph_ready_block sums each transaction's gas_limit into a per-space U256 accumulator before the gas-limit bound checks run. gas_limit is not bounded from above on the block-verification path (only the transaction pool caps it, which a block producer bypasses), so a crafted block can drive the running sum past U256. cfx_types::U256 panics on overflow and release builds enable overflow-checks, so the bare += aborts block processing instead of rejecting the block.

check_hard_gas_limit repeats the pattern one level down via total_gas.map_sum (native + evm), which overflows when each per-space sum fits but their total does not, so hardening only the loop would leave this site reachable.

Use checked_add at both sites and reject with InvalidPackedGasLimit on overflow. This changes no valid block's outcome: checked_add equals + for every in-range input, and an out-of-range total exceeds the block gas limit and is rejected anyway, so no transition height or CIP gate is required.

Add red-green regression tests for the same-space (loop) and cross-space (map_sum) overflow sites.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
