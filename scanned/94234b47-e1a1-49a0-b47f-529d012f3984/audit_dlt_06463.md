# [H] User Can Claim More Than totalAmount Due to Lack of Max Return Amount Check in _vested Function

## Summary
Severity: High
Chain: Smart contract
Component: Tapioca
Published: 2024-06-05
Source: https://github.com/hats-finance/Tapioca-0xe0b920d38a0900af3bab7ff0ca0af554129f54ad/issues/39
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x5caa93ee07135e02720c099e9d01cc00ad866269213415a65a670bd24d932afe
**Severity:** high

**Description:**
**Description**\
The `_vested` function in the Vesting contract has a potential issue where users can claim more than the total vested amount due to improper logic handling of initial unlock and  no max return value check(refer POC)

**Attack Scenario**\
if the user deposits 500,000 tokens with initialUnlockAmount 50,000 then user can claim ~549000 tokens(i.e ~49k extra tokens) just before the end of duration

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
```
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.23;

import "forge-std/Test.sol";
//import "../src/Vesting.sol";


contract TapiocaTest is Test{


    //alex:
    //totalAmout = 500,000;
    //initial unlock = 10% i.e 50,000
    //duration = 4 years

    uint256 public start = 1717575083;//current timestamp i.e 5 june 2024
   
    uint256 public  cliff = 0;
    
    uint256 public duration = 4*365 days;//duration of 4 years

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Tapioca-0xe0b920d38a0900af3bab7ff0ca0af554129f54ad/issues/39_
