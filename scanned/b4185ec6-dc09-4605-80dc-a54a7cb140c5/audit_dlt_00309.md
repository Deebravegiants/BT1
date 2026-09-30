# [M] EL-2026-20: Compiler does not check success of certain precompile calls

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Vyper Compiler
Source: https://notes.ethereum.org/B0rZmpzNTHeQY0FqACZ_Dw
Type: ef-disclosure

## Details
Short description *
1 sentence description of the bug
The vyper compiler does not check the success of certain calls to precompiles.
Attack scenario *
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
An attacker might be able to provide a contract with a very specific amount of gas where the precompile call fails, but the overall execution succeeds. This can lead to incorrect results.
Impact *
 Describe the effect this may have in a production setting
Potentially Incorrect Execution of Existing, Deployed Contracts. However, Likelihood seems relatively low.
Components *
Point to the files, functions, and/or specific line numbers where the bug occurs
https://github.com/vyperlang/vyper/blob/0abcf452b29f5348cb14233fd9a8444224392184/vyper/builtins/functions.py#L784 and https://github.com/vyperlang/vyper/blob/0abcf452b29f5348cb14233fd9a8444224392184/vyper/codegen/core.py#L328
Reproduction *
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
https://gist.github.com/ritzdorf/2e931de9403e57ff93bc547f2f000cce
