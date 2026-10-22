# [M] FM_BC_Bancor_Redeeming_VirtualSupply_v1 may get initialised in a way that will brick the contract

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-16
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/139
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** rnemes4
**Submission hash (on-chain):** 0xc4e1d972c648049ac67f27cf0ab33d445e5b01968a8160c3b54ba91721fb017e
**Severity:** medium

**Description:**
**Description**\
In the `FM_BC_Bancor_Redeeming_VirtualSupply_v1.init()` function it is possible to initialise with a combination of Issuance token decimals and initial issuance supply that will leave the contract in a state where it is impossible to call the `buy` function without it reverting.

**Attack Scenario**\
`init()` is called with an issuance token having 19 decimals and the virtualIssuanceSupply is set to 1 (in this scenraio it should have been set to at least 10)
Bob tries to make a `buy` with any deposit value, but the function will revert due to the code at line 400 returning zero:

```Solidity
FM_BC_Tools._convertAmountToRequiredDecimal(
                virtualIssuanceSupply, issuanceTokenDecimals, eighteenDecimals
            ),
```

being called with:
virtualIssuanceSupply = 1
issuanceTokenDecimals = 19
eighteenDecimals = 18

This will return 0 as proven by the following unit test

```Solidity
function testDecimalConversion() public {
        // Ensure the inputs are within valid ranges
        uint amount = 1;
        uint8 tokenDecimals = 19;
        uint8 requiredDecimals = 18;

        // Call the function with the base amount
        uint resultBase = _convertAmountToRequiredDecimal(
            amount,
            tokenDecimals,
            requiredDecimals
        );

        // Ensure the result is correct
        assertTrue(resultBase == 0, "Decimal conversion failed");
    }
```

This Zero value is then passed as the first argument to the call to `formula.calculatePurchaseReturn` in the following function.

```Solidity
    function _issueTokensFormulaWrapper(uint _depositAmount)
        internal
        view
        override(BondingCurveBase_v1)
        returns (uint mintAmount)
    {
        // Calculate mint amount through bonding curve
        uint decimalConvertedMintAmount = formula.calculatePurchaseReturn(
            // decimalConvertedVirtualIssuanceSupply
            FM_BC_Tools._convertAmountToRequiredDecimal(
                virtualIssuanceSupply, issuanceTokenDecimals, eighteenDecimals
            ),
            // decimalConvertedVirtualCollateralSupply
            FM_BC_Tools._convertAmountToRequiredDecimal(
                virtualCollateralSupply,
                collateralTokenDecimals,
                eighteenDecimals
            ),
            reserveRatioForBuying,
            // decimalConvertedDepositAmount
            FM_BC_Tools._convertAmountToRequiredDecimal(
                _depositAmount, collateralTokenDecimals, eighteenDecimals
            )
        );
        // Convert mint amount to issuing token decimals
        mintAmount = FM_BC_Tools._convertAmountToRequiredDecimal(
            decimalConvertedMintAmount, eighteenDecimals, issuanceTokenDecimals
        );
    }
```

`calculatePurchaseReturn` will then revert due to the fact `_supply` has been rounded down to Zero

```Solidity
function calculatePurchaseReturn(
        uint _supply,
        uint _connectorBalance,
        uint32 _connectorWeight,
        uint _depositAmount
    ) public view returns (uint) {
        // validate input
        require(
            _supply > 0 && _connectorBalance > 0 && _connectorWeight > 0
                && _connectorWeight <= MAX_WEIGHT
        );
```

**Attachments**

1. **Proof of Concept (PoC) File**
Add the following test to the E2E test suit, which will revert with

```Bash
├─ [462] BancorFormula::calculatePurchaseReturn(0, 3, 333333 [3.333e5], 100000000000000000000000 [1e23]) [staticcall]
    │   │   │   └─ ← [Revert] EvmError: Revert

```

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

contract BondingCurveFundingManagerE2EPOCChangeIssuance is E2ETest {
    // Module Configurations for the current E2E test. Should be filled during setUp() call.
    IOrchestratorFactory_v1.ModuleConfig[] moduleConfigurations;

    ERC20Issuance_v1 issuanceToken;

    address alice = address(0xA11CE);
    uint aliceBuyAmount = 200e18;

    address bob = address(0x606);
    uint bobBuyAmount = 100_000e18;

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
            decimals: 19,
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

    function test_e2e_OrchestratorFundManagementPOCChangeIssuance() public {
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

        token.mint(bob, bobBuyAmount);

        uint buf_minAmountOut =
            fundingManager.calculatePurchaseReturn(bobBuyAmount);

        console.log("buf_minAmountOut: ", buf_minAmountOut);

        uint bobTokenBalanceBefore = token.balanceOf(bob);
        console.log("Bob token balance before: ", token.balanceOf(bob));

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

        
    }
}

```

2. **Revised Code File (Optional)**
3. **Recommendation**
Add a check to the `init()` function to ensure that the `virtualIssuanceSupply` is initialised to a minimum amount compatibale with the relative token decimals.  i.e if Issuance token has 19 Decimals the the `virtualIssuanceSupply` should be at least `1e1 or 10 (1e(issuance token decimals - 18))`
