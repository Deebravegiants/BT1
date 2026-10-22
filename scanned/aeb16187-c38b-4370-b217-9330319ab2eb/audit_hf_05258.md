# [H] no_validation_on_reactiondeadline_allows_multiple_griefing_scenarios

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23460
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a creator creates a game they send an array of bytes32 `promptHash` variables associated with the questions:

```solidity
function createGame(
    uint256 _startTime,
    uint256 _endTime,
    uint256 _ticketPrice,
    uint256 _creatorFee,
    address _token,
    address _creatorFeeReceiver,
    bytes32[] memory _promptHashes, // <-----
    address[] memory _promptStrategies,
    address _sessionStrategy,
    address _rewardStrategy,
    bool _verificationRequired
) external returns (uint256 gameId) {...}
```

These `promptHash` values are then revealed in the `_revealPrompt` function when the creator calls `startAndRevealGameQuestion` or `revealGameQuestion`. The `_revealPrompt` checks:

```
keccak256(abi.encodePacked(_prompt, _salt)) == promptInitData.promptHash
```

and calls `revealQuestion` in the strategies:

```solidity
function revealQuestion(bytes memory question, uint256 questionId) external {
    Prompt memory q = abi.decode(question, (Prompt)); // <------
    require(registry.engageProtocols(msg.sender), InvalidSessionManager(msg.sender));
    require(q.sessionManager == msg.sender, OnlySessionManager(q.sessionManager, msg.sender));
    (, address promptStrategy) = SessionManager(q.sessionManager).questionCommitment(questionId);
    require(promptStrategy == address(this), InvalidPromptCall(questionId, promptStrategy));
    revealedQuestions[questionId] = q;
    revealedAt[questionId] = block.timestamp;
}
```

The input parameter `bytes memory question` is decoded into the `Prompt` struct:

```solidity
struct Prompt {
    address sessionManager;
    uint256 gameId;
    string questionText;
    uint256 reactionDeadline; // <-----
    string finalizedAnswer;
    string[] media; // <------
    string[] choices; // <------
}
```

**Impact**  
* the possible range of values for `reactionDeadline` is never validated; if the game creator sets it to `0` or `type(uint256).max` then answering questions will always revert; users will be unable to earn xp but the game can still be concluded by the game creator in order to prevent users from claiming refunds from their fees  
* `media` and `choices` should be validated to have the same length; creator owner can make mistakes setting up the questions and don't set properly this values making users harder to respond and probably lead to loss of funds (since users have not the choices and media set up they probably answer wrong).  
Both cases can result in loss of funds for users.

## Proof of Concept
```solidity
function test_zero_reactionDeadline() public {
    question.reactionDeadline = 0;
    bytes memory qEncoded = abi.encode(question);
    bytes32 questionHash = keccak256(abi.encodePacked(qEncoded, salt));
    promptHashes[0] = questionHash;
    promptStrategies[0] = promptStrategy;
    _createGame();
    _startGame();
    _warpToEndTime();
    sessionManager.endGame(1);
}
```

## Recommendation
Validate that:  
• `string[] media` and `string[] choices` are equal in length  
• `reactionDeadline` is within an admin‑controlled minimum & maximum range  
• `reactionDeadline` does not extend past a game's `endTime`
