# [H] SessionManager Out-of-Gas due to Excessive Questions

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23468
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Since there are no restrictions on the number of questions a game can support, a game could have so many questions that it causes `SessionManager::cancelGameIfCreatorMissing` and `endGame` to revert due to out‑of‑gas errors.

`endGame` iterates over all questions:

```solidity
function endGame(uint256 _gameId) external onlyState(_gameId, SessionState.Ongoing) {
    require(block.timestamp >= games[_gameId].endTime, GameIsNotEnded(games[_gameId].endTime,
    block.timestamp));
    uint256[] storage questions = gameQuestions[_gameId];
    for (uint256 i = 0; i < questions.length; i++) {
        require(_isRevealed(questions[i]), QuestionNotRevealed(_gameId, questions[i]));
    }
    games[_gameId].state = SessionState.Ended;
    emit GameEnded(_gameId);
}
```

`cancelGameIfCreatorMissing` has a similar loop:

```solidity
function cancelGameIfCreatorMissing(uint256 _gameId) external {
    require(
        games[_gameId].state != SessionState.Cancelled,
        InvalidGameState(SessionState.Cancelled, games[_gameId].state)
    );
    require(
        games[_gameId].state != SessionState.Concluded,
        InvalidGameState(SessionState.Concluded, games[_gameId].state)
    );
    require(block.timestamp >= games[_gameId].endTime, GameIsNotEnded(games[_gameId].endTime,
    block.timestamp));
    uint256[] storage questions = gameQuestions[_gameId];
    for (uint256 i = 0; i < questions.length; i++) {
        if (!_isRevealed(questions[i])) {
            games[_gameId].state = SessionState.Cancelled;
            emit GameCancelled(_gameId);
            return;
        }
    }
    revert GameWaitingForConclusion(_gameId);
}
```

If the number of questions is large enough, the loops can exceed the gas limit, causing the functions to revert.

## Recommendation
Limit the number of questions in a game.
