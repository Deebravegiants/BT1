# [M] vyper performs multiple eval of `sqrt()` argument built in

## Summary
Severity: Medium
Chain: Vyper
Component: vyper
CVE: CVE-2024-32649
CWE: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-5jrj-52x8-m64h
Type: github-advisory

## Details
### Summary
Using the `sqrt` builtin can result in multiple eval evaluation of side effects when the argument has side-effects. The bug is more difficult (but not impossible!) to trigger as of 0.3.4, when the unique symbol fence was introduced (https://github.com/vyperlang/vyper/pull/2914).

A contract search was performed and no vulnerable contracts were found in production.

### Details
It can be seen that the `build_IR` function of the `sqrt` builtin doesn't cache the argument to the stack: 
https://github.com/vyperlang/vyper/blob/4595938734d9988f8e46e8df38049ae0559abedb/vyper/builtins/functions.py#L2151

As such, it can be evaluated multiple times (instead of retrieving the value from the stack).

### PoC
With at least Vyper version `0.2.15+commit.6e7dba7` the following contract:
```vyper
c: uint256

@internal
def some_decimal() -> decimal:
    self.c += 1
    return 1.0

@external
def foo() -> uint256:
    k: decimal = sqrt(self.some_decimal())
    return self.c
```
passes the following test:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;

import "../../lib/ds-test/test.sol";
import "../../lib/utils/Console.sol";
import "../../lib/utils/VyperDeployer.sol";

import "../ITest.sol";

contract ConTest is DSTest {
```

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-5jrj-52x8-m64h_
