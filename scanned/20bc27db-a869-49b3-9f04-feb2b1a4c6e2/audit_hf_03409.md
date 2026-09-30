# [H] missing `isEpochClaimed` validation

## Summary
Severity: High
Contest weight: 0.4936
Dataset id: 18526
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing validation of the isEpochClaimed flag when rewards are claimed from the internal _claimRewards function. In the public claimRewards entry point the contract correctly checks the isEpochClaimed mapping and reverts if the epoch has already been claimed, but the internal function is also invoked by moveStakedLiquidity without performing the same check. The root cause is that the internal reward‑distribution routine does not verify whether the rewards for the given epoch have already been paid, and the flag validateEpoch_ only guards against claiming future epochs, not against duplicate claims. An attacker can first call claimRewards to receive the legitimate reward for a specific epoch, and then call moveStakedLiquidity, which internally calls _claimRewards for the same epoch with validateEpoch_ set to false. Because the isEpochClaimed mapping is not consulted, the contract transfers the reward a second time. This can be repeated each time the user moves liquidity, effectively allowing unlimited double‑claiming of rewards for a single epoch. The impact is inflation of reward tokens and loss of value for the protocol and honest participants, as the same reward pool is drained multiple times. The issue manifests whenever a token owner invokes moveStakedLiquidity (or any other function that calls _claimRewards without the proper guard) after an epoch has already been claimed. It affects token owners who can exploit the bug, as well as the overall protocol because the unearned rewards reduce the pool available to other users. The flaw was discovered during a Code4rena audit by reviewing the control flow of reward claims and noticing that the internal function lacked the isEpochClaimed revert that the external entry point contains. The problem is subtle because the internal function appears to perform all necessary accounting and the missing check is hidden behind a flag that only validates epoch range, making it easy to overlook during testing. To remediate, the contract should either add an explicit isEpochClaimed revert inside _claimRewards regardless of the validateEpoch_ flag, or ensure that every external call that reaches _claimRewards first checks the mapping, for example by inserting a require statement in moveStakedLiquidity before invoking the internal function. This change restores the invariant that each epoch’s rewards can be claimed at most once, aligning the implementation with the intended accounting logic where users receive a single reward per epoch and preventing the reward pool from being drained by repeated claims.

## Proof of Concept
The _claimRewards function is using to calculate and send the reward to the caller but this function is no validating if isEpochClaimed mapping is true due that in claimRewards function is validated, see the stament in the following lines:
    
    file: ajna-core/src/RewardsManager.sol
    function claimRewards(
            uint256 tokenId_,
            uint256 epochToClaim_ 
        ) external override {
            StakeInfo storage stakeInfo = stakes[tokenId_];
    
            if (msg.sender != stakeInfo.owner) revert NotOwnerOfDeposit(); 
    
            if (isEpochClaimed[tokenId_][epochToClaim_]) revert AlreadyClaimed(); // checking if the epoch was claimed;
    
            _claimRewards(
                stakeInfo,
                tokenId_,
                epochToClaim_,
                true,
                stakeInfo.ajnaPool
            );
        }

Now the moveStakedLiquidity is calling _claimRewards too without validate isEpochClaimed mapping:
    
    file: ajna-core/src/RewardsManager.sol
    function moveStakedLiquidity(
            uint256 tokenId_,
            uint256[] memory fromBuckets_,
            uint256[] memory toBuckets_,
            uint256 expiry_
        ) external override nonReentrant {
            StakeInfo storage stakeInfo = stakes[tokenId_];
    
            if (msg.sender != stakeInfo.owner) revert NotOwnerOfDeposit(); 
    
            uint256 fromBucketLength = fromBuckets_.length;
            if (fromBucketLength != toBuckets_.length)
                revert MoveStakedLiquidityInvalid();
    
            address ajnaPool = stakeInfo.ajnaPool;
            uint256 curBurnEpoch = IPool(ajnaPool).currentBurnEpoch();
    
            // claim rewards before moving liquidity, if any
            _claimRewards(stakeInfo, tokenId_, curBurnEpoch, false, ajnaPool); // no checking is isEpochClaimed is true and revert

Also we can see in the _claimRewards function there is no validation is isEpochClaimed is true, this allow a malicius user claimReward first and then move his liquidity to other bucket or the same bucket claiming the reward each time that he want.
    
    function _claimRewards(
            StakeInfo storage stakeInfo_,
            uint256 tokenId_,
            uint256 epochToClaim_,
            bool validateEpoch_,
            address ajnaPool_
        ) internal {
            // revert if higher epoch to claim than current burn epoch
            if (
                validateEpoch_ &&
                epochToClaim_ > IPool(ajnaPool_).currentBurnEpoch()
            ) revert EpochNotAvailable();
    
            // update bucket exchange rates and claim associated rewards
            uint256 rewardsEarned = _updateBucketExchangeRates(
                ajnaPool_,
                positionManager.getPositionIndexes(tokenId_)
            );
    
            rewardsEarned += _calculateAndClaimRewards(tokenId_, epochToClaim_);
    
            uint256[] memory burnEpochsClaimed = _getBurnEpochsClaimed(
                stakeInfo_.lastClaimedEpoch,
                epochToClaim_
            );
    
            emit ClaimRewards(
                msg.sender,
                ajnaPool_,
                tokenId_,
                burnEpochsClaimed,
                rewardsEarned
            );
    
            // update last interaction burn event
            stakeInfo_.lastClaimedEpoch = uint96(epochToClaim_);
    
            // transfer rewards to sender
            _transferAjnaRewards(rewardsEarned);
        }

## Recommendation
Check if the isEpochClaimed is true and revert in the _claimReward function
    
    if (isEpochClaimed[tokenId_][epochToClaim_]) revert AlreadyClaimed();

The series of calls they are suggesting are possible:  
stake  
claimRewards() -> get rewards  
moveStakedLiquidity() -> get rewards

What the finding also implies, is that if the _claimRewards function is called during moveStakedLiquidity without checking isEpochClaimed, a user could claim rewards multiple times for the same epoch.
