# [M] Improper Limit Enforcement Al-

## Summary
Severity: Medium
Contest weight: 0.6188
Dataset id: 1756
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contest README states that, in integer mode, there is a maximum of 10 NFTs per
address.
Maximum 10 NFTs per address in integer mode
Integer-based allocation limits (max 10 NFTs)
However, in the code implementation, users can bypass the intended 10 NFT per address
limit when isIntegerAllowance is set to true. This occurs because the limit is only
checked during each individual allocation call, not cumulatively across multiple calls. A
user can make multiple allocation calls, each under the 10 NFT limit, to acquire more
than 10 NFTs in total.
The insufficient enforcement of the 10 NFT per address limit stems from a flaw in the
contract's logic. The check for the limit (require(nftQuantity<=10,'Canonlystake10NFTsa tmaxinintegerallowance');) is performed only within the _allocate function and only
considers the number of NFTs requested in a single call, not the total number of NFTs
already allocated to that address.
```solidity
function _allocate(uint256 nftQuantity) internal {
    uint256 stakeAmount = nftQuantity * stakePrice;
    require(
        totalStakeReceived + stakeAmount <= maxTotalStakeable,
        'Exceeds max total allowable stake'
    );
    if (isIntegerAllowance) {
        require(nftQuantity <= 10, 'Can only stake 10 NFTs at max in integer allowance');
    }
    _transferToContract(_msgSender(), stakeAmount);
    totalStakeReceived += stakeAmount;
    nftMintAllowance[_msgSender()] += nftQuantity;
    totalNftToMint[_msgSender()] += nftQuantity;
    userStakeAmount[_msgSender()] += stakeAmount;
    emit Allocation(_msgSender(), nftQuantity);
}
```
ontracts/EwmNftAllowance.sol#L91-L109
Internal pre-conditions
External pre-conditions
Attack Path
1. The contract admin sets isIntegerAllowance to true.
2. An attacker repeatedly calls the whitelistedAllocation function, each time
requesting a number of NFTs upto 10.
3. The attacker successfully accumulates more than 10 NFTs, bypassing the intended
limit.
This bypass undermines the intended allocation mechanism. The contract's stated
limitation of 10 NFTs per address is not enforced, potentially leading to unfair distribution
and a depletion of the total available NFTs.

## Recommendation
The most effective mitigation is to modify the _allocate function to check the total
number of NFTs already allocated to an address before allowing a new allocation. This
requires tracking the total allocated NFTs for each address, either through a dedicated
mapping or by modifying the existing totalNftToMint variable to accurately reflect the
cumulative allocation, even after releaseNftStake is called.
This would require a change to how releaseNftStake updates totalNftToMint. A robust
solution would also ensure that the totalNftToMint variable is accurately updated even
after the releaseNftStake function is executed. This ensures the contract's behavior
aligns with the documentation.
Example of Mitigation (Aggregate Allocation):
Replace the whitelistedAllocation and _allocate functions with something like this:
```solidity
function whitelistedAllocation(uint256 nftQuantity, bytes32[] calldata merkleProof) public virtual whenNotPaused onlyDuringAllocation nonReentrant {
    require(checkWhitelist(_msgSender(), merkleProof), 'proof invalid');
    _allocate(nftQuantity);
}
function _allocate(uint256 nftQuantity) internal {
    require(nftQuantity > 0, "NFT quantity must be greater than zero");
    if (isIntegerAllowance) {
        require(nftQuantity <= 10, "Can only stake a maximum of 10 NFTs in integer allowance mode.");
    }
    uint256 currentAllowance = nftMintAllowance[_msgSender()];
    require(currentAllowance + nftQuantity <= 10, "Total allocation exceeds 10 NFTs."); //Check against 10 NFT limit
    uint256 stakeAmount = nftQuantity * stakePrice;
    require(totalStakeReceived + stakeAmount <= maxTotalStakeable, 'Exceeds max total allowable stake');
    _transferToContract(_msgSender(), stakeAmount);
    totalStakeReceived += stakeAmount;
    nftMintAllowance[_msgSender()] += nftQuantity;
    totalNftToMint[_msgSender()] += nftQuantity;
    userStakeAmount[_msgSender()] += stakeAmount;
    emit Allocation(_msgSender(), nftQuantity);
}
```
This revised code prevents the bypass by ensuring that the total number of NFTs
allocated to an address never exceeds 10 when isIntegerAllowance is true. The user must
request all their NFTs in a single transaction. This is a much more robust solution than the
original implementation.
