# [H] gameEndTime is incorrectly updated during unpause

## Summary
Severity: High
Contest weight: 0.5966
Dataset id: 9384
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The pause/unpause mechanism fails to adjust the game end time to account for elapsed time during pauses. When unpausing, the contract calculates gameEndTime using pausedAt + countdown instead of considering the actual pause duration. If a game is paused long enough, it will end immediately upon unpausing, declaring the last player before pause as the winner without giving other players the chance to participate. Consider the following scenario: 1. Game starts at timestamp 1000 with gameStartTime = 1000 and countdown = 300 seconds 2. Initial gameEndTime = 1300 3. At timestamp 1005, Player A presses the button - countdown decreases to 270 seconds (after 30-second decrement) - gameEndTime is updated to 1005 + 270 = 1275 - lastPlayer = Player A 4. At timestamp 1010, the game is paused for maintenance - pausedAt = 1005 (timestamp of last press) 5. The game remains paused for 500 seconds until timestamp 1510 6. At timestamp 1510, the game is unpaused - gameEndTime is incorrectly set to pausedAt + countdown = 1005 + 270 = 1275 7. Since timestamp 1510 > gameEndTime 1275, the game immediately ends 8. Player A is declared the winner without other players having a chance to compete

## Recommendation
It is suggested to implement the following changes:
```solidity
function pause() external override onlyRole(PAUSER_ROLE) {
    uint40 lastPeriod = lastPress != 0 ? lastPress : gameStartTime;
    duration = gameEndTime - block.timestamp;
    _pause();
}

/// @inheritdoc IButton
function unpause() external override onlyRole(PAUSER_ROLE) {
    gameEndTime = block.timestamp + duration;
    duration = 0;
    _unpause();
}
```
