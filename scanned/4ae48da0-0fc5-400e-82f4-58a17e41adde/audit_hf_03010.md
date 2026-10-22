# [M] Only part of `keccak256`

## Summary
Severity: Medium
Contest weight: 0.1928
Dataset id: 16828
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At 2 places in the code only part of the output of `keccak256()` is used as the hash:

  * At `TokenDistributor` - `DistributionState.distributionHash15` - uses only a 15 bytes as a hash

    * This one is intended to save storage
  * At `Crowdfund.governanceOptsHash` a 16 bytes is used as hash

    * This one has no benefit at all as it doesn’t save on storage

15/16 bytes hash is already not very high to begin with (as explained below). On top of that, using a non standard hash can be unsafe. Since diverging from the standard can break things.

For the `FixedGovernanceOpts` an attacker can create a legitimate party, and then when running `buy()` use the malicious hash to:

  * include himself in the hosts (DoS-ing the party by vetoing every vote)
  * reduce the `passThresholdBps` (allowing him to pass any vote, including sending funds from the Party)
  * Setting himself as `feeRecipient` and increasing the fee

For the `DistributionInfo` struct - an attacker can easily drain all funds from the token distribution contract, by using the legitimate hash to create a distribution with a malicious ERC20 token (and a malicious party contract), and then using the malicious hash to claim assets of a legitimate token.

## Recommendation
Use the standard, 32-bytes, output of `keccak256()`.

At first we dismissed this as being really impractical but the more we thought of what an attack would actually look like, the more practical (if still improbable) it would be. We will extend both hashes to full-width (32 bytes).

Agree with Medium risk. This attack seems unlikely but may be within the realm of possible when high value is at stake.

[0xble (PartyDAO) resolved](https://github.com/code-423n4/2022-09-party-findings/issues/231#issuecomment-1264680753):

Resolved: <https://github.com/PartyDAO/partybidV2/pull/138>
