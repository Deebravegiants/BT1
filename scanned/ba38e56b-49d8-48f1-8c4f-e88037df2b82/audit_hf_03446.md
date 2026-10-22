# [M] `depositETHOverTargetWeight`

## Summary
Severity: Medium
Contest weight: 0.6375
Dataset id: 18847
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logic flaw in the way it determines the next pool that will receive excess ETH deposits. When the manager contract has insufficient balance to fund a full validator (i.e., ethToDeposit is less than the required ETH_PER_NODE), the function poolAllocationForExcessETHDeposit still updates the global pointer poolIdArrayIndexForExcessDeposit before exiting. Because the selectedPoolCapacity array is filled with zeros, the pointer is advanced even though no actual allocation can be performed. An attacker can exploit this by sending a trivial amount of ETH (for example, 1 wei) to trigger the allocation routine, causing the pointer to roll over to the next pool index. In the following round the protocol will treat the rolled‑over index as the preferred pool and will allocate the attacker’s validator there, even though the contract’s balance is still insufficient for a normal allocation. This results in an unfair prioritisation of the attacker’s validator, effectively allowing a malicious participant to manipulate the round‑robin allocation order and capture validator slots that should have been unavailable. The impact is a breach of the protocol’s accounting assumptions: funds appear to disappear from the perspective of honest participants because their validators are not selected, while the attacker’s validator is incorrectly accepted. The vulnerability manifests only when the manager’s ETH balance is zero or lower than the per‑node requirement and when the excess‑deposit routine is called. It is difficult to notice because the state change is a single index variable and the malicious transfer can be as small as one wei, leaving no obvious on‑chain trace of a large fund movement. The issue was discovered during a manual audit that examined the allocation loop and the conditions under which poolIdArrayIndexForExcessDeposit is set. To remediate, the contract should revert if the allocation calculation yields only zeros, or it should update the pointer only when there is at least one validator that can actually be funded. Adding an explicit check that ethToDeposit >= ETH_PER_NODE before advancing the index, or resetting the index to its previous value when no allocation occurs, would close the attack surface and restore the intended fair round‑robin distribution of validator slots.

## Proof of Concept
`poolIdArrayIndexForExcessDeposit` is used to save `depositETHOverTargetWeight()`, which `Pool` is given priority for allocation in the next round.

The current implementation rolls over to the next `pool`, regardless of whether the current balance is sufficient or not.

`poolAllocationForExcessETHDeposit`:

```solidity
function poolAllocationForExcessETHDeposit(uint256 _excessETHAmount)
    external
    override
    returns (uint256[] memory selectedPoolCapacity, uint8[] memory poolIdArray)
{
..
    for (uint256 j; j < poolCount; ) {
        uint256 poolCapacity = poolUtils.getQueuedValidatorCountByPool(poolIdArray[i]);
        uint256 poolDepositSize = ETH_PER_NODE - poolUtils.getCollateralETH(poolIdArray[i]);
        uint256 remainingValidatorsToDeposit = ethToDeposit / poolDepositSize;
        selectedPoolCapacity[i] = Math.min(
            poolAllocationMaxSize - selectedValidatorCount,
            Math.min(poolCapacity, remainingValidatorsToDeposit)
        );
        selectedValidatorCount += selectedPoolCapacity[i];
        ethToDeposit -= selectedPoolCapacity[i] * poolDepositSize;
        i = (i + 1) % poolCount;
        //For ethToDeposit < ETH_PER_NODE, we will be able to at best deposit one more validator
        //but that will introduce complex logic, hence we are not solving that
        if (ethToDeposit < ETH_PER_NODE || selectedValidatorCount >= poolAllocationMaxSize) {
            poolIdArrayIndexForExcessDeposit = i;
            break;
        }    
```

Suppose now, the balance of `StaderStakePoolsManager` is 0 and `poolIdArrayIndexForExcessDeposit` = 1

If I have a `Validator` with funds to be allocated at `pool` = 2, I can maliciously transfer 1 wei and let `poolIdArrayIndexForExcessDeposit` roll over to 2.

This way, the next round of funding will be allocated in favor of my `Validator`.

Normally, if the current funds are not enough to allocate one `Validator`, then `poolIdArrayIndexForExcessDeposit` should not be rolled over. This is fairer.

Suggested: If `poolAllocationForExcessETHDeposit()` returns all 0’s, revert to avoid rolling `poolIdArrayIndexForExcessDeposit`.

## Recommendation
```solidity
function depositETHOverTargetWeight() external override nonReentrant {
    ..
    
    bool findValidator;
    for (uint256 i = 0; i < poolCount; i++) {
        uint256 validatorToDeposit = selectedPoolCapacity[i];
        if (validatorToDeposit == 0) {
            continue;
        }
        findValidator = true;
        address poolAddress = IPoolUtils(poolUtils).poolAddressById(poolIdArray[i]);
        uint256 poolDepositSize = staderConfig.getStakedEthPerNode() -
            IPoolUtils(poolUtils).getCollateralETH(poolIdArray[i]);

        lastExcessETHDepositBlock = block.number;
        //slither-disable-next-line arbitrary-send-eth
        IStaderPoolBase(poolAddress).stakeUserETHToBeaconChain{value: validatorToDeposit * poolDepositSize}();
        emit ETHTransferredToPool(i, poolAddress, validatorToDeposit * poolDepositSize);
    } 
    require(findValidator,"not valid validator");
```
