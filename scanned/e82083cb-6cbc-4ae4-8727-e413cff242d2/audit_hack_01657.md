# [M] BetHash incident: BetHash's betting game mechanism allows players to guess the ratio of the number between 0-100 and the random number given by the

## Summary
Severity: Medium
Target: BetHash
Loss: -
Attack method: Malicious Code Injection Attack
Published: 2019-11-07
Source: https://cmichel.io/what-really-happened-with-the-eos-play-hack/
Type: slowmist-incident

## Details
BetHash's betting game mechanism allows players to guess the ratio of the number between 0-100 and the random number given by the system to win the bonus of the corresponding odds. The smaller the bet number, the greater the odds. Every time a player makes a bet, the dicereceipt() function of the BetHash smart contract will be called to notify the player's account. At this point, the hacker can control the malicious program to hijack the notification and embed the inline operation to implement the attack. Although the attacker also needs to pay a certain amount of bet for every attack, as long as it keeps 0.1 EOS and is conservative
