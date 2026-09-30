# [H] Predictable Results For Dice Rolling

## Summary
Severity: High
Contest weight: 0.6340
Dataset id: 12453
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Dice contract, there is an Admin account acting as croupier for the game. The Admin plays a critical role in starting/ending a dice rolling round and sending the secret to reveal the dice rolling result. To elaborate, we show below the sendSecret() and _safeSendSecret() routines in the Dice contract.
```solidity
function sendSecret(uint256 epoch, uint256 bankSecret) public onlyAdmin whenNotPaused {
    Round storage round = rounds[epoch];
    require(round.lockBlock != 0, "End round after round has locked");
    require(round.status == Status.Lock, "End round after round has locked");
    require(block.number >= round.lockBlock, "Send secret after lockBlock");
    require(block.number <= round.lockBlock.add(intervalBlocks), "Send secret within intervalBlocks");
    require(round.bankSecret == 0, "Already revealed");
    require(keccak256(abi.encodePacked(bankSecret)) == round.bankHash, "Bank reveal not matching commitment");
    _safeSendSecret(epoch, bankSecret);
    _calculateRewards(epoch);
}

function _safeSendSecret(uint256 epoch, uint256 bankSecret) internal whenNotPaused {
    Round storage round = rounds[epoch];
    round.secretSentBlock = block.number;
    round.bankSecret = bankSecret;
    uint256 random = round.bankSecret ^ round.betUsers ^ block.difficulty;
    round.finalNumber = uint32(random % 6);
    round.status = Status.Claimable;
    emit SendSecretRound(epoch, block.number, bankSecret, round.finalNumber);
}
```
Before each round, the Admin will provide a hashed secret and the value will be stored at round.bankHash. After the round is locked, the Admin will send the bankSecret by calling sendSecret() to check if the hashed value of bankSecret matches the the stored round.bankHash, and then it would trigger the _safeSendSecret() to reveal the finalNumber. However, if we take a close look at _safeSendSecret(), this speciﬁc routine computes the round.finalNumber based on a random number generated from round.bankSecret ^ round.betUsers ^ block.difficulty. Since the round.bankSecret is provided by the Admin, the block.difficulty is hard-coded in certain blockchains (e.g. BSC), and the round.betUsers is possibly colluding with Admin, the result for the dice rolling may become predictable. If so, the game will become unfair and Banker's funds may be drained round by round as the Admin would inform the colluding users to bet a maximum amount allowed on the finalNumber.

## Recommendation
Add the block.timestamp to feed the random seed.
