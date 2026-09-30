# [M] Minting is not properly tracked, leading to inability to mint token when due

## Summary
Severity: Medium
Reporter: 0xacnologiac
Contest weight: 0.6591
Dataset id: 4595
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the function mint(), the timelock will be allowed to mint after 1 year from deployment. With a yearly mintcap to cap supply growth, The currentYearStart start is also updated. The issue here is that currentYearStart in the new year is set to whenever the block.timestamp is, after 365 days have passed. This is a wrong methodology for tracking the yearly emissions, because minting will sometimes not occur on the "new mint" year's date. This means asides the first year, yearly minting cannot happen because every delay in the first mint of the "mint" year will spill over to next and the next.
Impact: Let's assume a new DERC20 token is launched in March, 2025:
• The next mint can only start from March, 2026.
• if the proposal for the new mint through the governance timelock doesn't pass on time (till May 2026).
• The next minting for 2027 should also be due in March, 2027.
• This cannot happen because the currentYear start is now in May, so the new proposal has to wait till May 2027.
• assuming there is a shift in the new minting execution, the new time for the following mint will also shift.
• Meaning the current year is actually not being tracked, therefore minting cannot start on time.

## Proof of Concept
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
import { Test, console } from "forge-std/Test.sol";
import { Airlock, ModuleState } from "src/Airlock.sol";
import { IUniswapV3Factory } from "@v3-core/interfaces/IUniswapV3Factory.sol";
import {
    UniswapV3Initializer,
    SenderNotAirlock,
    PoolAlreadyInitialized,
    PoolAlreadyExited,
    OnlyPool,
    CallbackData,
    InitData
} from "src/UniswapV3Initializer.sol";
import { UniswapV2Migrator, IUniswapV2Router02, IUniswapV2Factory } from "src/UniswapV2Migrator.sol";
import { TokenFactory } from "src/TokenFactory.sol";
import { GovernanceFactory } from "src/GovernanceFactory.sol";
import { DERC20 } from "src/DERC20.sol";
import {
    WETH_MAINNET,
    UNISWAP_V3_FACTORY_MAINNET,
    UNISWAP_V3_ROUTER_MAINNET,
    UNISWAP_V2_FACTORY_MAINNET,
    UNISWAP_V2_ROUTER_MAINNET
} from "test/shared/Addresses.sol";

contract V3PocTest is Test {
    UniswapV3Initializer public initializer;
    Airlock public airlock;
    UniswapV2Migrator public uniswapV2LiquidityMigrator;
    TokenFactory public tokenFactory;
    GovernanceFactory public governanceFactory;
    address public airLockAdmin;

    // HAVE MAINNET_RPC_URL SET IN .env
    function setUp() public {
        vm.createSelectFork(vm.envString("MAINNET_RPC_URL"), 21_093_509);
        airLockAdmin = address(0xabbabababab);
        vm.startPrank(airLockAdmin);
        airlock = new Airlock(airLockAdmin);
        initializer = new UniswapV3Initializer(address(airlock), IUniswapV3Factory(UNISWAP_V3_FACTORY_MAINNET));
        uniswapV2LiquidityMigrator = new UniswapV2Migrator(
            address(airlock),
            IUniswapV2Factory(UNISWAP_V2_FACTORY_MAINNET),
            IUniswapV2Router02(UNISWAP_V2_ROUTER_MAINNET)
        );
        tokenFactory = new TokenFactory(address(airlock));
        governanceFactory = new GovernanceFactory(address(airlock));
        address[] memory modules = new address[](4);
        modules[0] = address(tokenFactory);
        modules[1] = address(governanceFactory);
        modules[2] = address(initializer);
        modules[3] = address(uniswapV2LiquidityMigrator);
        ModuleState[] memory states = new ModuleState[](4);
        states[0] = ModuleState.TokenFactory;
        states[1] = ModuleState.GovernanceFactory;
        states[2] = ModuleState.PoolInitializer;
        states[3] = ModuleState.LiquidityMigrator;
        airlock.setModuleState(modules, states);
        vm.stopPrank();
    }

    function test_v3_poc() public {
        // Deploy new token with tokenFactory
        uint256 initialSupply = 1_000_000e18;
        address[] memory recipients = new address[](4);
        recipients[0] = address(0x123);
        recipients[1] = address(0x124);
        recipients[2] = address(0x125);
        recipients[3] = address(0x126);
        uint256[] memory amounts = new uint256[](4);
        for (uint256 i = 0; i < 4; i++) {
            amounts[i] = initialSupply / 100;
        }
        bytes memory data = abi.encode(
            "DERC1 Token",
            "DT1",
            initialSupply,
            1 days,
            recipients,
            amounts
        );
        vm.startPrank(address(airlock));
        address assetDT =
        tokenFactory.create(initialSupply, airLockAdmin, airLockAdmin, bytes32(0), data);
        console.log("assetDT: ", assetDT);
        vm.stopPrank();
        vm.startPrank(airLockAdmin);
        DERC20 dt = DERC20(assetDT);
        assertEq(dt.owner(), airLockAdmin);
        vm.warp(dt.mintStartDate() + 7 weeks);// After first year, let's assume it takes 7 weeks for the mint proposal to pass
        dt.mint(airLockAdmin, 1_000_000e18);
        // Second year, proposal passes in 2 weeks to mint half of the yearly mint cap
        vm.warp(dt.mintStartDate() + 365 days + 2 weeks);
        // Reverts with ExceedsYearlyMintCap() even though another year has passed since start of minting
        dt.mint(airLockAdmin, 500_000e18);
    }
}
```
This test reverts with the following message:
Failing tests:
Encountered 1 failing test in test/shared/V3PocTest.sol:V3PocTest
[FAIL: ExceedsYearlyMintCap()] test_v3_poc() (gas: 2172932)
This is because the currentAnnualMint has not been reset even though enough time has passed.
Recommendation (optional): for the fix:
• Initalize currentYearStart to block.timetamp in the constructor.
• Modify the mint function as follows:
```solidity
function mint(address to, uint256 value) external onlyOwner {
    require(block.timestamp >= mintStartDate, MintingNotStartedYet());
    // @audit new year should start from the end of the previous year
    if (block.timestamp >= currentYearStart + 365 days) {
        currentYearStart += 365 days;
        currentAnnualMint = 0;
    }
    require(currentAnnualMint + value <= yearlyMintCap, ExceedsYearlyMintCap());
    currentAnnualMint += value;
    _mint(to, value);
}
```

## Recommendation
No data
