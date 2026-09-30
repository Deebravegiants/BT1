# [H] DoS of funds if a depositId was overriden then revoked

## Summary
Severity: High
Reporter: 0xAlix2, also found by zraxx, 0xAlix2 and 0xAlix2
Contest weight: 0.8155
Dataset id: 4961
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the earning power of a specific deposit ID goes below a threshold which is: ( uint256(_earningPower) * BIPS < minQualifyingEarningPowerBips * _balance ) then anyone can call enactOverride to move the delegation to the default deposit ID to make sure the delegators still get rewards. To make this profitable for the caller anyone who calls this function will get tips in shares. However, since we are minting shares this will cause the initial balance of the depositor to go down however the delegated balance of the user ( balanceCheckpoint ) will stay the same, which is greater than the user's initial balance and will cause the unstake to always revert with underflow when calculating the undelegated balance.

## Proof of Concept
```solidity
function testFuzz_cantUnstakeBalance() public {
    address _holder = makeAddr("holder");
    address _delegatee = makeAddr("delegate address");
    address _tipReceiver = makeAddr("tip receiver");
    uint256 _amount = 100e18;
    uint160 _tipAmount = 20000;
    uint256 _minQualifyingEarningPowerBips = 10_000;
    _mintUpdateDelegateeAndStake(_holder, _amount, _delegatee);
    _setMaxOverrideTip();
    _setMinQualifyingEarningPowerBips(_minQualifyingEarningPowerBips);
    // Set deposit earning power below threshold
    Staker.DepositIdentifier _depositId = lst.depositForDelegatee(_delegatee);
    // update min power
    earningPowerCalculator.__setEarningPowerForDelegatee(_delegatee, 0);
    // Force the earning power on the deposit to change
    vm.prank(address(lst));
    staker.stakeMore(_depositId, 0);
    // override
    lst.enactOverride(_depositId, _tipReceiver, _tipAmount);
    (uint96 _depositBalance,,,,,,) = staker.deposits(_depositId);
    // Earning power should always be equal to balance
    uint256 _earningPower = _depositBalance;
    earningPowerCalculator.__setEarningPowerForDelegatee(_delegatee, _earningPower);
    // Force the earning power on the deposit to change
    vm.prank(address(lst));
    staker.stakeMore(_depositId, 0);
    lst.revokeOverride(_depositId, _delegatee, _tipReceiver, _tipAmount);
    _unstake(_holder, 1e18);
}
```

## Recommendation
Calculate the delegated balance ( the balanceCheckpoint ) so that it will be:
```solidity
uint256 _delegatedBalance = _min(_calcBalanceOf(_holderState, _totals), _holderState.balanceCheckpoint);
```
