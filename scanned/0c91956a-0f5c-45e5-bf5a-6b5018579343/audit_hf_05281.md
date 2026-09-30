# [C] impossible_to_claim_rewards_when_ranked_rewards_or_number_of_winners_are_not_set,_resulting_in_permanently_locked_tokens_once_game_has_concluded

## Summary
Severity: Critical
Contest weight: 0.0000
Dataset id: 23522
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: FixedRanksReward::setRankedRewards enforces that ranked rewards can only be set when the game is in the Created state:
```solidity
function setRankedRewards(uint256 sessionId, uint256[] calldata _rankedRewards) external {
    require(sessionManager.getSessionState(sessionId) == SessionState.Created,
    NotCreated(sessionId));
    // ...
}
```
The same is also true for ProportionalToXPReward::setNumberOfWinners.  
But SessionManager::startAndRevealGameQuestion will happily start the game without ranked rewards / number of winners being set, and the game will progress all the way to the final Concluded state, giving the appearance that everything is OK.  

Impact: Once the game has concluded, when the winners try to claim their rewards this will revert with RankedRewardsNotSet or NumberOfWinnersMismatch. There is no way to claim the rewards and because the game is in the Concluded state it can't be cancelled - the tokens are permanently locked in the contract.

## Proof of Concept
```solidity
function test_setRankedRewardsNotCalled_gameStarted_gameConcludes_cantClaimRewards() public {
    _createGame();
    _startGame();
    _revealQuestion();
    _warpToEndTime();
    sessionManager.endGame(1);
    _concludeGame();
    vm.expectRevert(); // RankedRewardsNotSet(1)
    vm.prank(contestants[0]);
    sessionManager.claimRewards(1, 0);
}
```

## Recommendation
Recommended Mitigation: Don't allow the game to be started unless ranked rewards / number of winners have been set. Ideally:  
- the IRewardStrategy interface would have an external function `rewardsConfigured` which returns true if its rewards mechanism has been configured and false otherwise  
- FixedRanksReward and ProportionalToXPReward would both implement `rewardsConfigured` checking whether their internal reward implementations have been correctly configured  
- SessionManager::startAndRevealGameQuestion would call `rewardsConfigured` on its reward strategy and revert if it returned false.
