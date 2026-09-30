# [H] Py-EVM is vulnerable to arbitrary bytecode injection

## Summary
Severity: High
Chain: py-evm
Component: py-evm
CVE: CVE-2018-18920
CWE: Improper Restriction of Operations within the Bounds of a Memory Buffer
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-vqgp-4jgj-5j64
Type: github-advisory

## Details
Py-EVM v0.2.0-alpha.33 allows attackers to make a vm.execute_bytecode call that triggers computation._stack.values with '"stack": [100, 100, 0]' where b'\x' was expected, resulting in an execution failure because of an invalid opcode. This is reportedly related to "smart contracts can be executed indefinitely without gas being paid."
