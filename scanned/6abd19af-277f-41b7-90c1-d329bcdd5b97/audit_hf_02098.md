# [M] Potential Reentrancy Risk in Coin98Multisig::vote()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 11823
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [9] exploit, and the recent Uniswap/Lendf.Me hack [8]. We notice there is an occasion where the checks-effects-interactions principle is violated. Using the Coin98Multisig as an example, the vote() function (see the code snippet below) is provided to externally call a contract to execute the request if enough votes. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. Apparently, the interaction with the external contract (line 189) starts before effecting the update on internal states (lines 191 and 192), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the very same vote() function.
```solidity
function vote() isOwner(msg.sender) public override returns (bool) {
    VoteProgress memory progress = _voteProgress;
    require(progress.requestId > 0, "Coin98Multisig: No pending request");
    if (_votes[msg.sender] < progress.requestId) 
        _votes[msg.sender] = progress.requestId;
    progress.currentVote += _votePowers[msg.sender];
    _voteProgress = progress;
    emit Voted(msg.sender, progress.requestId, progress.currentVote, progress.requiredVote);
    if (progress.currentVote >= progress.requiredVote) {
        Request memory req = _request;
        (bool success, ) = req.destination.call{value: req.value}(req.data);
        if (success) {
            delete _request;
            delete _voteProgress;
            Executed(true, progress.requestId, req.destination, req.value, req.data);
        } else {
            Executed(false, progress.requestId, req.destination, req.value, req.data);
        }
    }
    return true;
}
```

## Recommendation
Apply necessary reentrancy prevention by making use of the common nonReentrant modifier.
