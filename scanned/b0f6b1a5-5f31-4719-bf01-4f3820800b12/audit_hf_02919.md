# [M] SQDR-1 | No Check For Max Players

## Summary
Severity: Medium
Contest weight: 0.0293
Dataset id: 16244
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing validation in the player registration function of the betting contract. The function registerPlayer allows any address to be added to the list of participants without checking whether the current number of registered players has already reached the contract‑defined maximum (maxNumberOfPlayers). Because the contract does not enforce this upper bound, an attacker can submit an arbitrary number of registrations, causing the internal array of players to grow without limit. Functions that later iterate over the player list, such as the prize‑distribution routine in SquidBetPrizePool, will then have to process a potentially unbounded number of entries. When the array becomes large enough, the gas required for a single iteration exceeds the block gas limit, causing the transaction to revert. This results in a denial‑of‑service condition: legitimate winners cannot be paid, the prize pool cannot be settled, and the protocol appears to be stuck. The issue manifests when the contract is used under normal conditions but an adversary deliberately floods the registration phase. Users experience symptoms such as “my winnings are not paid out” or “the prize claim transaction runs out of gas and fails”, even though they have correctly placed bets. The bug was discovered during a manual audit that examined the registration logic and noted the absence of a comparison against maxNumberOfPlayers. It can be hard to notice because the registration function itself succeeds and does not revert, giving the impression that everything works, while the problem only appears later during payout. The root cause is a missing input validation check, a classic example of an unchecked limit leading to resource exhaustion. To remediate, the contract should enforce the maximum player count by adding a require statement that compares the current length of the player array with maxNumberOfPlayers before pushing a new entry. This simple guard prevents the array from growing beyond the intended size and eliminates the DoS vector. The vulnerability belongs to the class of “unbounded array growth” or “missing bounds check” bugs that break business logic assumptions about participant limits and can cause accounting failures and loss of service.

## Recommendation
Add the check in registerPlayer.
