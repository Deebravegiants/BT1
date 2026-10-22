# [M] Overshadowing and Uncaptured Returns

## Summary
Severity: Medium
Source: https://github.com/matter-labs/system-contracts/blob/4ad1f26ae205d5a973216d141833e0ac37d72ec8/bootloader/bootloader.yul
Type: audit-issue

## Details
In the [bootloader contract](https://github.com/matter-labs/system-contracts/blob/4ad1f26ae205d5a973216d141833e0ac37d72ec8/bootloader/bootloader.yul), the function `setTxOrigin` has a return value `success`, which is overshadowed by a [local variable](https://github.com/matter-labs/system-contracts/blob/4ad1f26ae205d5a973216d141833e0ac37d72ec8/bootloader/bootloader.yul#L1478) of the same name within the function scope. In the `solc` Solidity compiler this triggers a compiler error.

Additionally, the `setTxOrigin` function is called from the [top level without capturing its return value](https://github.com/matter-labs/system-contracts/blob/4ad1f26ae205d5a973216d141833e0ac37d72ec8/bootloader/bootloader.yul#L333), which causes another compiler error in `solc` and might lead to unexpected outcomes when using other compilers.

The same issue applies to the `precompileCall` function, which has a return value that is not captured when it is called inside the `nearCallPanic` function.

To address these issues, consider removing all unused return values.

_**Update:** Resolved in [pull request #135](https://github.com/matter-labs/system-contracts/pull/135/) at commit [45c04f9](https://github.com/matter-labs/system-contracts/pull/135/commits/45c04f9f774f0cdc46ef3e3f1f8380b5673ebb04)._
