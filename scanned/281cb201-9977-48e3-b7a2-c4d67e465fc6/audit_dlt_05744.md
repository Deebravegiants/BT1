# [H] # Attackathon _ Fuel Network 33248 - [Smart Contract - High] Incorrect Implementation of IFP Floor and

## Summary
Severity: High
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033248%20-%20%5BSmart%20Contract%20-%20High%5D%20Incorrect%20Implementation%20of%20IFP%20Floor%20and%20Ceil%20Functions.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway-libs/tree/0f47d33d6e5da25f782fc117d4be15b7b12d291b

## Description

## Fuel Network bug report

### Incorrect Implementation of IFP Floor and Ceil Functions

#### Description

The current implementation of the floor and ceil functions in `sway-libs` for the signed Fixed Point numbers is flawed. The implementation returns the wrong number for every negative input.

### Root Cause

The `floor` function from the `IFP64` implementation is as follows:

```rs
    pub fn floor(self) -> Self {
        if self.non_negative {
            self.trunc()
        } else {
            let trunc = self.underlying.trunc();
            if trunc != UFP32::zero() {
                self.trunc() - Self::from(UFP32::from(1u32))
            } else {
                self.trunc()
            }
        }
    }
```

Similarly, the `ceil` function is implemented as:

```rs
    pub fn ceil(self) -> Self {
        let mut underlying = self.underlying;
        let mut non_negative = self.non_negative;

```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033248%20-%20%5BSmart%20Contract%20-%20High%5D%20Incorrect%20Implementation%20of%20IFP%20Floor%20and%20Ceil%20Functions.md_
