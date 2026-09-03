# [H] # Attackathon _ Fuel Network 33039 - [Smart Contract - High] The subtraction function is not correctly

## Summary
Severity: High
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033039%20-%20%5BSmart%20Contract%20-%20High%5D%20The%20subtraction%20function%20is%20not%20correctly%20implemented%20for%20signed%20integers%20which%20can%20lead%20to%20incorrect%20values%20being%20calculated.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway-libs/tree/0f47d33d6e5da25f782fc117d4be15b7b12d291b

## Description

## Brief/Intro

In the subtraction functions for signed integers in the Sway libraries, the case when the `other` parameter is negative is handled incorrectly. When the `other` parameter is negative, it is still simply subtracted instead of being added, as would be mathematically correct.

## Vulnerability Details

In the sway-libs, within the signed integer library, every signed integer has a subtraction function (see 1. reference. I have linked to the I64 subtraction function as an example, but the subtraction functions of all signed integers have the same bug). The parts of the function that handle cases where the `other` parameter is negative are incorrectly implemented (see 2nd and 3rd references). When the `other` parameter is negative, it is subtracted, but it should actually be added.

```rust
305:             res = Self::from_uint(self.underlying - Self::indent() + other.underlying);
```

This part of the code is responsible for when `self` is positive and `other` is negative. Here you can see that `self` and `other` are being added, but the problem is that `other` is added as a negative value. Therefore, `other` is subtracted from `self`. For the result to be calculated correctly, the absolute value of other (so it is no longer negative) should be added to self. It would look like this:

```rust
305:             res = Self::from_uint(self.underlying + (Self::indent() - other.underlying));
```

A similar error occurs when self and other both are negative:

```rust
313:             if self.underlying < other.underlying {
314:                 res = Self::from_uint(other.underlying - self.underlying + Self::indent());
315:             } else {
316:                 res = Self::from_uint(self.underlying + other.underlying - Self::indent());
317:             }
```

This part could be fixed like this:

```rust
313:             if self.underlying < other.underlying {
314:                 res = Self::from_uint((Self::indent - other.underlying) + self.underlying);
315:             } else {
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033039%20-%20%5BSmart%20Contract%20-%20High%5D%20The%20subtraction%20function%20is%20not%20correctly%20implemented%20for%20signed%20integers%20which%20can%20lead%20to%20incorrect%20values%20being%20calculated.md_
