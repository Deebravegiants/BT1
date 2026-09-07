# [M] Spearbit finding 5.2.2 not fixed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-tapioca
Published: 2024-03-18
Source: https://github.com/code-423n4/2024-02-tapioca-findings/issues/175
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token/blob/20a83b1d2d5577653610a6c3879dff9df4968345/contracts/options/TapiocaOptionBroker.sol#L408-L414
https://github.com/Tapioca-DAO/tap-token/blob/20a83b1d2d5577653610a6c3879dff9df4968345/contracts/options/TapiocaOptionBroker.sol#L292-L298


# Vulnerability details

## Description
The Spearbit finding "5.2.2 It is possible to exercise TAP option an extra time compared to lock duration" is not fixed. The finding itself is a follow up on the C4 finding [#189](https://github.com/code-423n4/2023-07-tapioca-findings/issues/189). The description of the issue can be found in the Spearbit report.

The mitigation introduced in the [PR](https://github.com/Tapioca-DAO/tap-token/pull/155) seems lost in the code base at audit here.

## Impact
Quoting the impact from the Spearbit report:
> Attacker has removed one epoch of rewards from the long term stakers, receiving 2 tapOFT payoffs for 1 epoch long staking. More generally, an attacker can add 1 epoch of option rewards in excess to their actual locking time (as epsilon can be made minutes long and not significant position locking wise).
> This is a violation of base protocol [token economy](https://docs.tapioca.xyz/tapioca/token-economy/token-economy#call-option-incentive-tap-otap:~:text=Lenders%20with%20active%20oTAP%20positions%20will%20receive%20oTAP%20shares%20from%20the%20DSO%20program%20every%20week%20that%20their%20position%20remains%20locked%2C%20proportional%20to%20their%20positions%20share%20of%20the%20total%20supplied%20locked%20liquidity%20in%20the%20respective%20market%2C):
>> Lenders with active oTAP positions will receive oTAP shares from the DSO program every week that their position remains locked, proportional to their positions share of the total supplied locked liquidity in the respective market

## Proof of Concept
Test showing the issue is still there in `tap-token/test/OptionTest.t.sol`:
```solidity
    function testExerciseOptionTwice() public {
        pearlmit.approve(address(yieldbox), 1, address(tOLP), type(uint200).max, type(uint48).max);
        paymentToken.mint(address(this),1000e18);
        paymentToken.approve(address(pearlmit),type(uint256).max);
        pearlmit.approve(address(paymentToken), 0, address(tOB), type(uint200).max, type(uint48).max);

        // epoch timestamps
        uint256 epoch2 = block.timestamp + 7 days;
        uint256 epoch3 = epoch2 + 7 days;

        // step 1 participate right before end of epoch
        vm.warp(epoch2 - 5 minutes);

        uint256 tOLPId = tOLP.lock({
            _to: address(this),
            _singularity: IERC20(singularity), 
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-tapioca-findings/issues/175_
