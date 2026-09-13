# [M] Signature verification failure in Tendermint

## Summary
Severity: Medium
Chain: github.com/tendermint/tendermint
Component: github.com/tendermint/tendermint
CWE: Improper Verification of Cryptographic Signature
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-f3w5-v9xx-rp8p
Type: github-advisory

## Details
_The root cause of this security vulnerability is in the Tendermint specification, and this advisory is a duplicate of https://github.com/tendermint/spec/security/advisories/GHSA-jqfc-687g-59pw._


### Impact
Tendermint light clients running versions 0.34.0 to 0.34.8 are unable to detect and punish a new kind of attack. We’re calling this a “forward lunatic attack,” or FLA. The severity of this vulnerability is _moderate_. 

Note that an FLA cannot be successfully executed unless there are already ⅓+ Byzantine validators, and therefore outside of Tendermint’s security model; however, it is important to be able to detect and punish these kinds of attacks in order to incentivize correct behavior.

In an FLA, an attacking validator (with ⅓+ voting power) signs commit messages for arbitrary application state associated with a block height that hasn’t been seen yet, hence the name “forward lunatic attacks.” A malicious validator effectively executes a [lunatic attack](https://docs.tendermint.com/master/spec/light-client/accountability/#the-misbehavior-of-faulty-validators), but signs messages for a target block that is higher than the current block. This can be dangerous: Typically, misbehavior evidence is only created when there are conflicting blocks at the same height, but by targeting a block height that is far “ahead” of the current chain height, it’s possible that the chain will not produce a (conflicting) block at the target height in time to create evidence. 

Prior to Tendermint v0.34.9, the light client could accept a bad header from its primary witness, and would not be able to form evidence of this deception, even if all the secondary witnesses were correct. Because the light client is responsible for verifying cross-chain state for IBC, a successful FLA could result in loss of funds. However, it is important to note that FLAs are only possible outside the Tendermint security model. 

All FLAs, attempted and successful, leave traces of provable misbehavior on-chain. A faulty header contains signatures from the faulty validator, and even in unpatched versions of Tendermint Core, networks could use social consensus (off-chain action) to recover the network. The patches introduced in Tendermint Core v0.34.9 handle all evidence automatically and on-chain. 

Note that this fix also allows for successful automatic reporting of FLAs, even after a chain halt. By adding a time to FetchBlock, light clients effectively have a backup way to determine if a halted chain should have continued, and it will be able to submit evidence as soon as the chain resumes. 

### Patches
This problem has been patched in Tendermint Core v0.34.9. 

### Workarounds
There are no workarounds. All users are recommended to upgrade to Tendermint Core v0.34.9 at their earliest possible convenience. 

### Credits

Thank you to @MaximilianDiez for originally surfacing this issue, and to @cmwaters, @josef-widder, and @milosevic for creating fixes at both the implementation and specification level.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [tendermint/tendermint](https://github.com/tendermint/tendermint)
* Email us at [security@tendermint.com](mailto:security@tendermint.com)
