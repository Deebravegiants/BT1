# [H] Reentrancy in `USDO.flashLoan

## Summary
Severity: High
Contest weight: 0.2095
Dataset id: 19083
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to a reentrancy attack vector, an attacker can flashLoan an unlimited amount of USDO. For example the attacker can create a malicious contract as the `receiver`, to execute the attack via the `onFlashLoan` callback (line 94 USDO.sol).

The exploit works because `USDO.flashLoan()` is missing a reentrancy protection (modifier).

As a result an unlimited amount of USDO can be borrowed by an attacker via the flashLoan exploit described above.

## Proof of Concept
Here is a POC that shows an exploit:

<https://gist.github.com/zzzitron/a121bc1ba8cc947d927d4629a90f7991>

To run the exploit add this malicious contract into the contracts folder:

<https://gist.github.com/zzzitron/8de3be7ddf674cc19a6272b59cfccde1>

## Recommendation
Consider adding some reentrancy protection modifier to `USDO.flashLoan()`.

Should be `High` severity, could really harm the protocol.
