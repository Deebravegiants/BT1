# [M] Unenforced staking requirement

## Summary
Severity: Medium
Source: https://github.com/neptune-mutual-blue/protocol/blob/73fc82fbe0d1388867b7df669983fe42760daeb1/contracts/libraries/VaultLibV1.sol#L151
Type: audit-issue

## Details
Adding liquidity requires a liquidity provider to have at least [a minimum amount of NPM tokens](https://github.com/neptune-mutual-blue/protocol/blob/73fc82fbe0d1388867b7df669983fe42760daeb1/contracts/libraries/VaultLibV1.sol#L151) staked in the vault.

However, the purpose and usefulness of this requirement is unclear, since it can be bypassed. In particular:

* there is no relationship between the amount of PODs created and the size of the stake
* PODs are transferable to unstaked users, so users can provide liquidity without staking
* staked users can [exit their entire staked amount](https://github.com/neptune-mutual-blue/protocol/blob/73fc82fbe0d1388867b7df669983fe42760daeb1/contracts/core/liquidity/VaultLiquidity.sol#L113-L118) without redeeming any PODs by calling `removeLiquidity` with parameters `podsToRedeem = 0`, `npmStakeToRemove = amount`, and `exit = 1`; the `exit = 1` is crucial as it allows execution of [line 234](https://github.com/neptune-mutual-blue/protocol/blob/73fc82fbe0d1388867b7df669983fe42760daeb1/contracts/libraries/VaultLibV1.sol#L234) of `VaultLibV1.sol`

Consider documenting and enforcing the intended relationship between NPM staking and liquidity provision.

**Update:** _Acknowledged, not fixed. The Neptune team stated:_

> _Although we plan to redo the staking requirement logic from scratch, we wish to consider this risk as acceptable for the time being._
