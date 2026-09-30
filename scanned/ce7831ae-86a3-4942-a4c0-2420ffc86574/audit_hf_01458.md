# [M] Centralization Risks

## Summary
Severity: Medium
Contest weight: 0.1736
Dataset id: 7590
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Given a malicious or compromised owner, user assets may be at risk in the following scenarios:
USDT to pay rewards for ongoing games can be withdrawn from the Vault via withdraw() at any time.
The vault can also be depleted by operators playing themselves and making them always win with big guess rate multipliers.
The gameFactory from the Vault can be changed at any time via setGameFactory() to later call transferPlayerRewards() with deceiving game information to claim any amount of rewards.
The montRewardManager from the Vault can be changed at any time via setMontRewardManager() to prevent transferPlayerRewards() from executing and reverting on player wins.
The minimumBetAmount and maximimBetRate values can be modified at any time in the Vault to prevent players from guessing cards.
The gameCreationFee in the GameFactory can be changed right before a game is created to take all the approved USDT from a player when calling createGame(). Other game settings that the player may not agree with can be changed at any time, right before they call createGame().

## Recommendation
Some suggestions to mitigate centralization risks:
Lock USDT rewards in the Vault when a bet is made via guessCard() until revealCard() or claimWin() are executed. Release the lock after it. This will make sure that there is enough liquidity to pay for ongoing bets.
Create a timelock contract and apply any changes to Vault and GameFactory settings after a certain time, so that users are aware of them. This will prevent changing the underlying logic of the system with new external contracts or setting unfair values.
