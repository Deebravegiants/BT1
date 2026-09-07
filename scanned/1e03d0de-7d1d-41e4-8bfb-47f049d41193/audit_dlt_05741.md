# [H] # Attackathon _ Fuel Network 33227 - [Smart Contract - High] Lack of overflow protection in the pow fu

## Summary
Severity: High
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033227%20-%20%5BSmart%20Contract%20-%20High%5D%20Lack%20of%20overflow%20protection%20in%20the%20pow%20functions%20for%20unsigned%20integers%20can%20lead%20to%20a%20loss%20of%20coins%20when%20calculating%20coin%20amounts.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway/tree/v0.61.2

## Description

## Brief/Intro

For the data types u8, u16, and u32, there is no overflow protection in the pow function implemented in the standard library. If the pow function is used to calculate coin amounts, it can result in the loss of coins.

## Vulnerability Details

For the data types `u8` `u16`, `u32`, `u64`, and `u256`, the pow function is implemented in the standard library in `math.sw`. However, the pow function for the data types `u8`, `u16`, and `u32` does not have overflow protections. An overflow of a `u64` and a `u256` is handled by the VM. Overflow protection for the other three data types would need to be implemented directly in the pow function in the standard library because the VM does not handle it. Due to the lack of these protections, the pow function of these data types are susceptible to overflow (see 1. reference). For `u16` and `u32`, the result would simply be larger than the data type as long as it still fits into a `u64`, since the VM converts `u16` and `u32` into u64's. For `u8`, there would be a simple wraparound, and once the result exceeds 255, it would start back at 0.

## Impact Details

This bug can have many different impacts based on what is calculated with the pow function. Especially if a coin amount is calculated with the pow function or if the result is further used to calculate a coin amount, it can easily lead to a loss of coins. Additionally, with the data types `u16` and `u32`, if the result exceeds the maximum of the data type, the value is still stored without wrapping. If this number is then returned and further used in the Rust SDK, it would wrap there, resulting in an incorrect value. This can again lead to a loss of coins if tokens are transfers based on this value.

## References

1. https://github.com/FuelLabs/sway/blob/ebc2ee6bf5d488e0ff693bfc8680707d66cd5392/sway-lib-std/src/math.sw#L114-L139

## Proof of concept

## Proof of Concept

For the PoC of this bug, a new fuel project with a Rust test suite is needed. This can be created with the following commands:

1. `forc new pow-bug`
2. `cd pow-bug`
3. `cargo generate --init fuellabs/sway templates/sway-test-rs --name pow-bug --force` Now the following code needs to be inserted into the `main.sw` file:

```rust
contract;

//Setup
use std::{
    asset::mint_to,
    constants::DEFAULT_SUB_ID
};
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2033227%20-%20%5BSmart%20Contract%20-%20High%5D%20Lack%20of%20overflow%20protection%20in%20the%20pow%20functions%20for%20unsigned%20integers%20can%20lead%20to%20a%20loss%20of%20coins%20when%20calculating%20coin%20amounts.md_
