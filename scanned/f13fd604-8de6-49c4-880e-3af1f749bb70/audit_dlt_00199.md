# [M] vyper performs double eval of raw_args in create_from_blueprint

## Summary
Severity: Medium
Chain: Vyper
Component: vyper
CVE: CVE-2024-32647
CWE: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-3whq-64q2-qfj6
Type: github-advisory

## Details
### Summary
Using the `create_from_blueprint` builtin can result in a double eval vulnerability when `raw_args=True` and the `args` argument has side-effects. 

A contract search was performed and no vulnerable contracts were found in production. In particular, the `raw_args` variant of `create_from_blueprint` was not found to be used in production.

### Details
It can be seen that the `_build_create_IR` function of the `create_from_blueprint` builtin doesn't cache the mentioned `args` argument to the stack: https://github.com/vyperlang/vyper/blob/cedf7087e68e67c7bfbd47ae95dcb16b81ad2e02/vyper/builtins/functions.py#L1847

As such, it can be evaluated multiple times (instead of retrieving the value from the stack).

### PoC
The vulnerability is demonstrated in the following `boa` test:
``` vyper
src1 = """
c: uint256
"""
deployer = """
created_address: public(address)
deployed: public(uint256)

@external
def get() -> Bytes[32]:
    self.deployed += 1
    return b''

@external
def create_(target: address):
    self.created_address = create_from_blueprint(target, raw_call(self, method_id("get()"), max_outsize=32), raw_args=True, code_offset=3)
"""

Factory = b.loads_partial(src1)
c = Factory.deploy_as_blueprint()

c2 = b.loads(deployer, b'')
c2.create_(c)
c2.deployed()
```
The output of `c2.deployed()` is `2` although `create_` was called only once and the value was initialized to `0`.

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-3whq-64q2-qfj6_
