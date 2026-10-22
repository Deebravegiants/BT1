# [H] SessionManager::revealGameQuestion doesn't validate that input _questionId belongs to input _- gameId

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23470
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SessionManager::revealGameQuestion doesn't validate that input _questionId belongs to input _gameId. It calls QuestionManager::_revealPrompt which ends up calling the revealQuestion function of the relevant prompt contract, but none of these verify that the input _questionId belongs to input _gameId.

## Recommendation
Verify that the input _questionId belongs to input _gameId and consider applying the same fix such that it is also enforced for `startAndRevealGameQuestion`. One way to do this is by adding this check inside `QuestionManager::_revealPrompt`:

```solidity
function _revealPrompt(uint256 _gameId, uint256 _questionId, bytes memory _prompt, uint256 _salt)
    internal {
    PromptInitData storage promptInitData = questionCommitment[_questionId];
    require(
        _gameId == promptInitData.sessionId,
        InvalidSessionIdForQuestion(_questionId, _gameId, promptInitData.sessionId)
    );
    // existing logic...
}
```

Consider also restricting functions such as `startAndRevealGameQuestion` and `revealGameQuestion` using the `onlyCreator` modifier – though technically this shouldn't be strictly necessary as only the game creator possesses the necessary salts.
