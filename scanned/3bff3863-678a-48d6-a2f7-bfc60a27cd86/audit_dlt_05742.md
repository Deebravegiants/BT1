# [M] # Attackathon _ Fuel Network 33233 - [Smart Contract - Medium] Incorrect Implementation of Unsigned -b

## Summary
Severity: Medium
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033233%20-%20%5BSmart%20Contract%20-%20Medium%5D%20Incorrect%20Implementation%20of%20Unsigned%20-bit%20Fixed%20Point%20Fractional%20Function.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway-libs/tree/0f47d33d6e5da25f782fc117d4be15b7b12d291b

## Description

## Fuel Network bug report

### Incorrect Implementation of Unsigned 32-bit Fixed Point Fractional Function

#### Description

The current implementation of the fractional function in `sway-libs` for the unsigned 32-bit Fixed Point and signed 64-bit Fixed Point is flawed. This issue causes the function to revert every time it's called, potentially leading to problems for projects built on the Fuel platform.

### Root Cause

The `fract` function from the `UFP32` implementation is as follows:

```rs
    pub fn fract(self) -> Self {
        Self {
            // first move to the left (multiply by the denominator)
            // to get rid of integer part, than move to the
            // right (divide by the denominator), to ensure 
            // fixed-point structure
            underlying: ((self.underlying << 16) - u32::max() - 1u32) >> 16,
        }
    }
```

The issue arises after the left shift operation, where the function subtracts `u32::max` and then subtracts `1`. Since left shifting doesn't change the operand's type (i.e., `a << 16` keeps a as `u32`), `(self.underlying << 16)` remains within the bounds of `u32`. Specifically, `(self.underlying << 16)` is constrained by `4294901760` (`0b11111111111111110000000000000000`), with the left shift ensuring the 16 rightmost bits are zero.

Consequently, for any `self.underlying`, `(self.underlying << 16)` is always less than `u32::max`, leading to an underflow and causing a revert.

### Impact

Every usage of `UFP32.fract` results in a revert, affecting:

1. `UFP32.ceil` - relies on the fract function.
2. `IFP64.fract` - internally uses UFP32, causing it to revert.

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033233%20-%20%5BSmart%20Contract%20-%20Medium%5D%20Incorrect%20Implementation%20of%20Unsigned%20-bit%20Fixed%20Point%20Fractional%20Function.md_
