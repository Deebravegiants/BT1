# [M] migrate() cannot do anything

## Summary
Severity: Medium
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L556
Type: audit-issue

## Details
# migrate() cannot do anything

## Summary

migrate() is called as an ordinary function. It therefore is unable to do anything differently from just having someone's wallet call migrate.

## Vulnerability Detail

See summary.

## Impact

The contract cannot be migrated

## Code Snippet

See how migrate() is called as an ordinary call. https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L556

Here is the relevant part of the disassembly, confirming that it uses the CALL opcode.

```plain

	1125    63    PUSH4 0x8fd3ab80 # migrate()
	112A    60    PUSH1 0x40
	112C    52    MSTORE
	112D    80    DUP1
	112E    3B    EXTCODESIZE
	112F    15    ISZERO
	1130    61    PUSH2 0x21d2
	1133    57    *JUMPI
	1134    60    PUSH1 0x00
	1136    60    PUSH1 0x40
	1138    60    PUSH1 0x04
	113A    60    PUSH1 0x5c
	113C    60    PUSH1 0x00
	113E    85    DUP6
	113F    5A    GAS
	1140    F1    CALL
```

## Tool used

Manual Review

## Recommendation

Presumably, the intention is to call migrate() as a delegatecall
