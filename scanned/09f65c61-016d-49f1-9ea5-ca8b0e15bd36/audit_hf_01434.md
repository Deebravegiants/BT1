# [M] FairLauncher inherits BlastNoYieldAdapter but will hold ETH

## Summary
Severity: Medium
Contest weight: 0.0386
Dataset id: 7446
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an incorrect inheritance hierarchy in the FairLauncher contract. FairLauncher is designed to receive Ether during token sales and, because it operates on the Blast network, any Ether held by the contract should generate yield that can be claimed by the protocol. However, FairLauncher inherits from BlastNoYieldAdapter, a base contract that deliberately disables the configuration required for the Blast address to make its yield claimable. As a result, the Ether accumulated in FairLauncher continues to earn yield on the Blast network, but the contract lacks the necessary logic to claim that yield, effectively locking the reward. This situation occurs whenever the contract holds Ether – typically after a sale – and later attempts to invoke any claim function that assumes yield is available. The impact is a loss of expected revenue: protocol operators and token holders see no increase in balance or reward distribution even though the underlying Ether is generating yield, violating the business assumption that deposited funds will accrue and be distributable. From a user perspective the UI may display a zero or missing reward amount despite a positive Ether balance, leading to confusion and a perception that the system is broken. The issue was discovered during a manual audit that compared the contract’s inheritance chain against the intended Blast reward flow and noticed the mismatch. It can be hard to notice because the contract does not revert or emit errors; the only symptom is the absence of expected yield, which may be attributed to normal market conditions. The bug belongs to a broader class of misconfiguration errors where a contract inherits a variant that disables a critical feature, thereby breaking business logic without obvious technical failures. To remediate the problem the contract should inherit from BlastAdapter, the version that configures the Blast address for claimable yield, or alternatively add the missing configuration steps from BlastAdapter into FairLauncher. This change restores the ability to claim the accrued yield, aligning the contract’s behavior with the protocol’s financial expectations.

## Recommendation
Inherit BlastAdapter instead of BlastNoYieldAdapter to claimed the yield from ETH.
