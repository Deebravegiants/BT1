# [H] Escaping losses by frontrunning the oracle updates

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-08-28
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/125
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0x1cbc5b4ccacf24a6894550780af43d53515a6b94f863bfe84c2aa536a2cc5713
**Severity:** high

**Description:**
## Description
To exit a vault, users have two options:
- If the vault contains ETH then user can call `redeem`.
- If all ETH is staked then user needs to call `enterExitQueue`.

The vault token to ETH exchange rate is determined by the profit/loss value updated by the oracles. Hence any delay in oracle updates can lead to issues for vault depositors.

In case the vault experiences slashing penalty, a user can try to exit the vault before the oracle reports the slashing loss. This can be done by monitoring the slashing event offchain and reacting to it as soon as it occurs. 

Ideally any loss should be shared among all depositors of the vault, but in this scenario early responders can escape the loss due to which all loss will be born by the late responders.


## Attack Scenario
- A vault gets deployed and Alex & Bob deposits 16 ETH each.
- A validator is created with the deposited 32 ETH.
- Charlie deposits 16 ETH to the vault.
- After that the validator receives slashing penalty of 9 ETH.
- Alex notices the slashing event and before the keeper oracle reports the loss of vault he calls `redeem` function.
- Alex successfully redeems the idle 16 ETH (deposited by Charlie) from the vault and leaves the system at no loss.
- Now Bob also notices the slashing event, but since there are no idle ETH in the vault he calls the `enterExitQueue` function. 16 ETH are accounted in exit queue for Bob.
- Charlie does nothing.
- Oracle update about the slashing loss gets posted on chain.
- After the exit period of ETH (~36 days), the vault receives 23 ETH (32 - 9).
- Bob invokes the `claimExitedAssets` and receives his ~16 ETH.
- Charlie exits the system and takes the complete 9 ETH loss individually.

Ideally all three users should have born the loss of 3 ETH each, but by front running the oracle update Alex and Bob were able to bypass the loss.

The issue exists due to two reasons:
1. Users can frontrun slashing oracle update and invoke `redeem`.
2. Users can frontrun slashing oracle update and invoke `enterExitQueue`.

## Mitigation

_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/125_
