# [H] FiveFiftyRule::_updateEntityAllowance rounds in wrong direction for entity allowance subtraction

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23297
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function _updateEntityAllowance is used to either increase/decrease the entity allowance based on where parameter add is true/false.  
When add == false, adjusted_amt is the amount to subtract. However, it is truncated because division is involved. This means that aData.allowance - adjusted_amt will be bigger than the true value.  
In the worse case scenario this can mean that the allowance is now too large and that a subsequent transfer to the entity will make it violate the 5/50 rule.

## Proof of Concept
### Diff showing the problematic logic
```diff
@@ -465,8 +465,8 @@ contract FiveFiftyRule is UUPSUpgradeable, AccessManagedUpgradeable {
 uint256 len = ents.length;
 for (uint256 i; i<len; ++i) {
 EntityData memory a = entityData[ents[i]];
- if (a.catalyst == inv &&
- (REMORA_PERCENT_DENOMINATOR / a.equity) * amount >
+ if (a.catalyst == inv &&
+ REMORA_PERCENT_DENOMINATOR * amount / a.equity >
 entityData[ents[i]].allowance
 ) return false;
 }
@@ -505,16 +505,16 @@ contract FiveFiftyRule is UUPSUpgradeable, AccessManagedUpgradeable {
 // to side changes
 if (to != address(0)) {
 IndividualData storage iTo = individualData[to];
-
+
 if (iTo.isEntity) { // if entity
- if (entityData[to].allowance <= amount) {
- entityData[to].allowance -= SafeCast.toUint64(amount);
+ if (entityData[to].allowance >= amount) {
+ entityData[to].allowance -= SafeCast.toUint64(amount);
 iTo.lastBalance += SafeCast.toUint64(amount);
 emit FiveFiftyApproved(from, to, amount);
 35
 return true;
 } else revert ();
```

### Full PoC contract
```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;
import "forge-std/console2.sol";
import {RemoraTestBase} from "../RemoraTestBase.sol";
import {FiveFiftyRule} from "../../../contracts/Compliance/FiveFiftyRule.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {SafeCast} from "@openzeppelin/contracts/utils/math/SafeCast.sol";
contract FiveFiftyRule_RoundingPoC is RemoraTestBase {
    FiveFiftyRule internal fiveFiftyRule;
    // helpers (same as your math discussion)
    uint256 constant DENOM = 1_000_000;
    function setUp() public override {
        RemoraTestBase.setUp();
        // Deploy rule and initialize
        fiveFiftyRule = FiveFiftyRule(address(new ERC1967Proxy(address(new FiveFiftyRule()), "")));
        fiveFiftyRule.initialize(address(accessMgrProxy), 0);
        // Allow our test to call restricted functions on fiveFiftyRule and child
        bytes4[] memory sel = new bytes4[](1);
        sel[0] = FiveFiftyRule.addToken.selector;
        accessMgrProxy.setTargetFunctionRole(address(fiveFiftyRule), sel, ADMIN_TOKEN_ID);
        accessMgrProxy.grantRole(ADMIN_TOKEN_ID, address(this), 0);
        bytes4[] memory cs = new bytes4[](2);
        cs[0] = bytes4(keccak256("setFiveFiftyCompliance(address)"));
        cs[1] = bytes4(keccak256("setLockUpTime(uint32)"));
        accessMgrProxy.setTargetFunctionRole(address(d_childTokenProxy), cs, ADMIN_TOKEN_ID);
        // Wire fiveFiftyRule to domestic child; remove lockup
        d_childTokenProxy.setFiveFiftyCompliance(address(fiveFiftyRule));
        d_childTokenProxy.setLockUpTime(0);
    }
    function test_RoundingDown_Allows_ExtraEntityToken_ExceedingLookThroughCap() public {
        // --------------------------
        // Parameters we use for the PoC
        // --------------------------
        // Total supply: large, so we can transfer a very large amount to the catalyst without violating the cap.,!
        // We'll target a 50% cap for the catalyst (to leave room for a huge direct transfer).
        uint64 totalSupply = 10_000_000;
        uint32 capPercent = 100_000;
        uint64 capAmountMicros = totalSupply * capPercent;
        uint64 equityMu = 333_334;
        uint256 ENTITY_BAL = 1_500_000;
        uint256 CATALYST_BAL = 499_999;
        centralTokenProxy.mint(address(this), totalSupply);
        fiveFiftyRule.addToken(address(centralTokenProxy));
        // Choose a catalyst (a domestic user) and an entity address
        address entity = getDomesticUser(0);
        address catalyst = getDomesticUser(1);
        address otherInvestor = getDomesticUser(2); // will never directly own any tokens in this example,!
        address[] memory investors = new address[](2);
        investors[0] = catalyst;
        investors[1] = otherInvestor;
        bytes4[] memory psel = new bytes4[](1);
        psel[0] = bytes4(keccak256("setMaxPercentIndividual(address,uint32)"));
        accessMgrProxy.setTargetFunctionRole(address(fiveFiftyRule), psel, ADMIN_TOKEN_ID);
        fiveFiftyRule.setMaxPercentIndividual(catalyst, capPercent);
        bytes4[] memory esel = new bytes4[](2);
        esel[0] = bytes4(keccak256("createEntity(address,address,uint64,uint64,address[])"));
        esel[1] = bytes4(keccak256("setCatalyst(bool,address,address,uint64,uint64)"));
        accessMgrProxy.setTargetFunctionRole(address(fiveFiftyRule), esel, ADMIN_TOKEN_ID);
        uint64 calculatedAllowance = SafeCast.toUint64(totalSupply * 1e6 * capPercent / equityMu);
        console2.log("calculatedAllowance: %s", calculatedAllowance);
        // Check that allowance is correct
        uint256 userProportion = calculatedAllowance * equityMu / 1e6;
        assertEq(userProportion, capAmountMicros - 1);
        uint256 exposure = uint256(ENTITY_BAL)* 1e6 * equityMu / 1e6 + CATALYST_BAL * 1e6;
        console2.log("exposure: %s", exposure);
        assertGe(exposure, capAmountMicros);
        fiveFiftyRule.createEntity(entity, catalyst, equityMu, calculatedAllowance, investors);
        centralTokenProxy.dynamicTransfer(entity, ENTITY_BAL);
        logEntity("0", entity);
        logIndividual("entity 0", entity);
        logIndividual("catalyst 0", catalyst);
        centralTokenProxy.dynamicTransfer(catalyst, CATALYST_BAL);
        logEntity("1", entity);
        logIndividual("entity 1", entity);
        logIndividual("catalyst 1", catalyst);
    }
    function logEntity(string memory s, address entity) internal view {
        FiveFiftyRule.EntityData memory ed = fiveFiftyRule.testing_entityData(entity);
        console2.log("--- EntityData %s ---", s );
        console2.log("catalyst: %s", ed.catalyst);
        console2.log("equity: %s", ed.equity);
        console2.log("allowance: %s", ed.allowance);
    }
    function logIndividual(string memory s, address individual) internal view {
        FiveFiftyRule.IndividualData memory id = fiveFiftyRule.testing_individualData(individual);
        console2.log("--- IndividualData %s ---", s);
        console2.log("isEntity: %s", id.isEntity);
        console2.log("numCatalyst: %s", id.numCatalyst);
        console2.log("groupId: %s", id.groupId);
        console2.log("customMaximum: %s", id.customMaximum);
        console2.log("lastBalance: %s", id.lastBalance);
    }
}
```

## Recommendation
Recommended Mitigation: The adjusted_amt must be rounded up when add == false.  
Update the code as below, assuming the existence of `_mulDivFloor` and `_mulDivCeil`, which round down/up respectively. It also includes the fix from Issue Divide before multiply loses precision in FiveFiftyRule::_updateEntityAllowance and leads to caps being exceeded.

```solidity
function _updateEntityAllowance(bool add, address inv, uint256 amount) internal returns (bool) {
    uint8 numCatalyst = individualData[inv].numCatalyst;
    uint256 len = findEntity[inv].length;
    for (uint256 i; i < len; ++i) {
        if (numCatalyst == 0) break;
        EntityData storage aData = entityData[findEntity[inv][i]];
        if (aData.catalyst != inv) continue;
        --numCatalyst;
        uint256 adjusted;
        if (add) {
            adjusted = _mulDivFloor(amount, REMORA_PERCENT_DENOMINATOR, aData.equity);
            aData.allowance += SafeCast.toUint64(adjusted);
        } else {
            adjusted = _mulDivCeil(amount, REMORA_PERCENT_DENOMINATOR, aData.equity);
            uint64 adj64 = SafeCast.toUint64(adjusted);
            if (adj64 > aData.allowance) return false;
            aData.allowance -= adj64;
        }
    }
    return true;
}
```
