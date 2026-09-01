# [H] # Attackathon _ Fuel Network 33242 - [Smart Contract - High] Incorrect Implementation of IFP Multiply

## Summary
Severity: High
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033242%20-%20%5BSmart%20Contract%20-%20High%5D%20Incorrect%20Implementation%20of%20IFP%20Multiply%20and%20Divide%20Functions.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway-libs/tree/0f47d33d6e5da25f782fc117d4be15b7b12d291b

## Description

## Fuel Network bug report

### Incorrect Implementation of IFP Multiply and Divide Functions

#### Description

The current implementation of the multiply and divide functions in `sway-libs` for the signed Fixed Point numbers is flawed. Specifically, the implementation always returns a positive number, even when a negative result is expected.

### Root Cause

The `multiply` function from the `IFP64` implementation is as follows:

```rs
    fn multiply(self, other: Self) -> Self {
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
            underlying: self.underlying * other.underlying,
            non_negative: non_negative,
        }
    }
```

Similarly, the `divide` function is implemented as:

```rs
    fn divide(self, divisor: Self) -> Self {
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033242%20-%20%5BSmart%20Contract%20-%20High%5D%20Incorrect%20Implementation%20of%20IFP%20Multiply%20and%20Divide%20Functions.md_
