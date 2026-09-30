# [M] MajorityChoicePrompt SessionManager Instance Conflict

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23449
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: MajorityChoicePrompt is supposed to support multiple instances of SessionManager, however every instance of SessionManager starts with `QuestionManager::nextQuestionId = 0`. This is problematic as `MajorityChoicePrompt::revealReaction` does this:  

```solidity
Reaction storage r = reactions[_questionId][_user];
require(!r.baseReaction.reactions[_questionId][_user], AnswerAlreadyRevealed(_user, _gameId, _questionId));
```  

When a user plays `questionId = 0` on the first instance of SessionManager everything will work ok and `reactions[_questionId][_user].revealed` will be set to true. If that same user plays `questionId = 0` on a second instance of SessionManager which uses the same instance of MajorityChoicePrompt, then `MajorityChoicePrompt::revealReaction` will revert with `AnswerAlreadyRevealed`.  

Another potential issue is that `results[questionId][player]` will have valid results stored for a player from games on the first instance and this mapping doesn't differentiate between the different instances of SessionManager.

## Recommendation
Recommended Mitigation: The simplest fix is that each SessionManager instances gets its own fresh MajorityChoicePrompt instance; the same issue likely affects SPBinaryPrompt and TriviaChoicePrompt.  

Another option is that:  
- there should only be 1 active instance of SessionManager at one time  
- when a new instance of SessionManager is made active, it should be initialized with `gameId`, `sessionId` and `questionId` that are greater than the previous active instance  
- add tests to the test suite which exercise this exact scenario to ensure everything will continue to work as expected
