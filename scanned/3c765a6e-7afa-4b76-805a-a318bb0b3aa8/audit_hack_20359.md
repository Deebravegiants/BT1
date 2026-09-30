# [C] 5.1.6 Insufficient check about division remainder

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** zkevm-rom:utils.zkasm#L
**Description:** ThedivARITHsubroutine uses the arithmetic state machine to perform division. The equation used
isA * B + C = D * 2**256 + E, all of those variables are 256-bit unsigned numbers, but the equation is an
equation on integers.
The subroutine computesE / AandE % Aat the same time (bothEandAare inputs to the subroutine and are
assigned like that to the variables of the state machine).
The subroutine performs two checks before it invokes the state machine. Those are:

- division by zero (A == 0), it directly returns(0, 0)


- E < A: In this case, it directly returns(0, E)
Then it invokes the state machine, settingD = 0,B = ${E/A}(free input),C = ${E%A}(free input).
Choosing these free inputs makes the state machine succeed.
The problem is that the remainder${E%A}is only a proper remainder if it is less thanA. If we for example invoke
the state machine withB = ${E/A - 1},C = ${(E%A) + A}, this will also satisfy the equation (as long asE/A >=
1 and we don’t get an arithmetic overflow).
In line 501, a comment states that this check "remainder < divisor" is performed after invoking the state machine,
but the code actually performs a different check: It invokes theLTstate machine onCandEand thus comparesC
< Einstead ofC < A.
**This means a malicious prover can forge invalid division and modulo operations.**
Note that due to the check againstE < Abefore invoking the state machine, we only invoke the state machine in
the case thatA <= Eand thus the invalid checkC < Eis never stricter than the correct checkC < A, which resulted
in this not being discovered in tests.
**Recommendation:** Change the code after line 501 from
C => A ; reminder
E => B ; divisor

to
A => B ; divisor
C => A ; remainder

**Polygon-Hermez:** Fixed in PR #205.
**Spearbit:** Acknowledged.
