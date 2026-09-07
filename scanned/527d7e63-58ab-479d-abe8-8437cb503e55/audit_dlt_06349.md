# [M] Unbounded proxy length in LootVoteController can cause function to become unusable

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-17
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/64
Type: hats-finding

## Details
**Github username:** @erictee2802
**Twitter username:** 0xEricTee
**Submission hash (on-chain):** 0x3ae2c165fcb7496616237c22e0f59abef3e4fedfb12d62aeafc904082777fb2f
**Severity:** medium

**Description:**
**Description**\

The proxy length in `LootVoteController.sol` is unbounded, and the length of proxy is looped in `LootVoteController::_clearExpiredProxies`.  Each time the function `LootVoteController::setVoterProxy` is called, a new proxy will be added to the `currentUserProxyVoters` array. If at some point there are now a large number of `proxies`, iterating over them will become very costly and can result in a gas cost that is over the block gas limit. This will mean that a transaction cannot be executed anymore, causing these functions in a state of DoS.




**Attack Scenario**\

Looping over unbounded array can result in a state of DoS.

**Attachments**

NA

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

- Install foundry.

- Rename the original test folder to `typescript-test` and create a new folder name `test`.

- Add `forge-std` module to lib with command: `git submodule add https://github.com/foundry-rs/forge-std lib/forge-std`

- Add `remappings.txt` file in `Vote-Flywheel` folder with the following content:
```
@ensdomains/=node_modules/@ensdomains/
@nomiclabs/=node_modules/@nomiclabs/
@openzeppelin/=node_modules/@openzeppelin/
@solidity-parser/=node_modules/@solidity-parser/
ds-test/=lib/forge-std/lib/ds-test/src/
eth-gas-reporter/=node_modules/eth-gas-reporter/
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/64_
