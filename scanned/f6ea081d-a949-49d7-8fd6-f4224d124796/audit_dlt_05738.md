# [H] # Attackathon _ Fuel Network 33168 - [Smart Contract - High] Incorrect Sign Determination In Multiply

## Summary
Severity: High
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033168%20-%20%5BSmart%20Contract%20-%20High%5D%20Incorrect%20Sign%20Determination%20In%20Multiply%20%20Divide%20Operations%20within%20IFP%20Implementations.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway-libs/tree/0f47d33d6e5da25f782fc117d4be15b7b12d291b

## Description

## Brief/Intro

During my audit of the IFP (signed fixed-point number) implementations in the sway-libs , this vulnerability were identified. This could lead to incorrect calculations in smart contracts relying on this implementation and cause massive losses.

## Vulnerability Details

Incorrect Sign Determination in Multiply & Division Operations in IFP128

The division operation incorrectly determines the sign of the result. the current implementation uses a logical condition that is always false, resulting in division operations always producing a positive result, regardless of the signs of the operands.

& the condition

`(self.non_negative && !self.non_negative) || (!self.non_negative && self.non_negative)`

in multiply & divide functions :

```

impl core::ops::Divide for IFP128 {
    /// Divide a IFP128 by a IFP128. Panics if divisor is zero.
    fn divide(self, divisor: Self) -> Self {
        let non_negative = if (self.non_negative
            && !self.non_negative)
            || (!self.non_negative
            && self.non_negative)
        {
            false
        } else {
            true
        };
        Self {
            underlying: self.underlying / divisor.underlying,
            non_negative: non_negative,
        }
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033168%20-%20%5BSmart%20Contract%20-%20High%5D%20Incorrect%20Sign%20Determination%20In%20Multiply%20%20Divide%20Operations%20within%20IFP%20Implementations.md_
