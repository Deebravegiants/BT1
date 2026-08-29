# [M] Holographable tokens can be reinitialized

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-holograph
Published: 2022-10-24
Source: https://github.com/code-423n4/2022-10-holograph-findings/issues/215
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-10-holograph/blob/f8c2eae866280a1acfdc8a8352401ed031be1373/contracts/enforcer/Holographer.sol#L147-L169


# Vulnerability details

When new holographable tokens are created, they typically set a state variable that holds the address of the holograph contract. When creation is done through the `HolographFactory`, the holograph contract is [passed in as a parameter](https://github.com/code-423n4/2022-10-holograph/blob/f8c2eae866280a1acfdc8a8352401ed031be1373/contracts/HolographFactory.sol#L252) to the holographable contract's initializer function. Under normal circumstances, this would ensure that the hologrpahable asset stores a trusted holograph contract address in its `_holographSlot`.

However, the initializer is vulnerable to reentrancy and the `_holographSlot` can be set to an untrusted contract address. This occurs because before the initialization is complete, the Holographer makes a [delegate call](https://github.com/code-423n4/2022-10-holograph/blob/f8c2eae866280a1acfdc8a8352401ed031be1373/contracts/enforcer/Holographer.sol#L162-L164) to a corresponding enforcer contract. From here, the enforcer contract makes an [optional call](https://github.com/code-423n4/2022-10-holograph/blob/f8c2eae866280a1acfdc8a8352401ed031be1373/contracts/enforcer/HolographERC20.sol#L241) to the source contract in an attempt to intialize it. This call can be used to reenter into the Holographer contract's initialize function before the first one has been completed and overwrite key variables such as the `_adminslot`, the `_holographSlot` and the `_sourceContractSlot`. 

One way in which this becomes problematic is because of how holographed ERC20s perform `transferFrom` calls. Holographed ERC20s by default allow two special addresses to [transfer](https://github.com/code-423n4/2022-10-holograph/blob/f8c2eae866280a1acfdc8a8352401ed031be1373/contracts/enforcer/HolographERC20.sol#L527) assets on behalf of other users without an allowance. These addresses are calculated by calling `_holograph().getBridge()` and `_holograph().getOperator()` respectively. With the above described reentrancy issue, `_holograph().getBridge()` and `_holograph().getOperator()` can return arbitrary addresses. This means that newly created holographed ERC20 tokens can be prone to unauthorized transfers. These assets will have been deployed by the HolographFactory and may look and feel like a safe holographable token to users but they can come with a built-in rugpull vector.

## Proof of Concept:
```
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../contracts/HolographFactory.sol";
import "../contracts/HolographRegistry.sol";
import "../contracts/Holograph.sol";
import "../contracts/enforcer/HolographERC20.sol";

//Contract used to show reentrancy in initializer
contract SourceContract {
    address public holographer;
    MockContract public mc;

    constructor() {
         mc = new MockContract();
    }

    //function that reenters the holographer and sets this contract as the new holograph slot
    function init(bytes memory initPayload) external returns(bytes4) {
        assembly {
            sstore(holographer.slot, caller())
        }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-10-holograph-findings/issues/215_
