# [H] # Attackathon _ Fuel Network 33195 - [Smart Contract - High] Incorrect Calculations in Subtraction Fun

## Summary
Severity: High
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033195%20-%20%5BSmart%20Contract%20-%20High%5D%20Incorrect%20Calculations%20in%20Subtraction%20Functions%20for%20Signed%20Integers.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway-libs/tree/0f47d33d6e5da25f782fc117d4be15b7b12d291b

## Description

## Fuel Network bug report

### Incorrect Calculations in Subtraction Functions for Signed Integers

#### Description

The current implementation of the subtraction function in the `sway-libs` for signed integers is incorrect. This can lead to erroneous calculations, potentially causing critical vulnerabilities in projects built on the Fuel platform.

### Root Cause

The way the signed numbers work in sway is by taking the indent of the unsigned counterparts and anything above it is positive while anything below is negative, so for example: The u8 range is `0-255` and the indent is `128` so 128 becomes 0 and `5 == 133`, `-5 == 123` and so on.

So to generalize, for every `x` the I8 underlying value will be `x + 128`.

Let's generalize even more, for every `x` the signed underlying value will be `x + indent`

Lets look at how a naive sub function would look:

The mechanism for handling signed integers in Sway involves using an offset (indent) based on the unsigned counterparts. For example, the range for `u8` is `0-255`, with an indent of `128`. Thus, `128` is mapped to `0`, `133` to `5`, and `123` to `-5`, and so forth.

In general terms, for any signed integer `x`, the underlying value is calculated as `x + indent`.

A naive subtraction function might be written as:

```rs
sub(a, b) => a - b => (a + indent) - (b + indent) => a - b
```

This approach loses the indent offset. Therefore, the correct general function should be:

```rs
sub(a, b) => a.underlying - b.underlyting + indent
```


_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033195%20-%20%5BSmart%20Contract%20-%20High%5D%20Incorrect%20Calculations%20in%20Subtraction%20Functions%20for%20Signed%20Integers.md_
