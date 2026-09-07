# [H] # Attackathon _ Fuel Network 33267 - [Smart Contract - High] Bug in Multiply and Divide function

## Summary
Severity: High
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033267%20-%20%5BSmart%20Contract%20-%20High%5D%20Bug%20in%20Multiply%20and%20Divide%20function.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway-libs/tree/0f47d33d6e5da25f782fc117d4be15b7b12d291b

## Description

## Brief/Intro

It seems that both multiply and divide function in `ifp64.sw`,`ifp128.sw`,`ifp256.sw` will not work correctly if any one of the number is negative as shown in below poc

## Location

https://github.com/FuelLabs/sway-libs/blob/0f47d33d6e5da25f782fc117d4be15b7b12d291b/libs/src/fixed\_point/ifp64.sw#L273-L276 https://github.com/FuelLabs/sway-libs/blob/0f47d33d6e5da25f782fc117d4be15b7b12d291b/libs/src/fixed\_point/ifp64.sw#L292-L295 Similarly for `ifp128.sw`,`ifp256.sw`

## Vulnerability Details

1. Lets see how resulting `non_negative` is calculated while multiplying and dividing

```sway
let non_negative = if (self.non_negative
            && !self.non_negative)
            || (!self.non_negative
            && self.non_negative)
        {
            false
        } else {
            true
        };
```

2. As we can see it is only checking `non_negative` param for 1st argument and not on the `other.non_negative`
3. So if we multiply -A \* B then `non_negative` becomes true since `(self.non_negative && !self.non_negative) || (!self.non_negative && self.non_negative)` always remain false
4. So result will be AB instead of -AB

## Impact Details

User who is trusting this library for arithmetic operation can bear huge losses since this will return resulting negative value as positive while multiplying and dividing

## Proof of concept


_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033267%20-%20%5BSmart%20Contract%20-%20High%5D%20Bug%20in%20Multiply%20and%20Divide%20function.md_
