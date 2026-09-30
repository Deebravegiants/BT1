# [M] Updating the state

## Summary
Severity: Medium
Contest weight: 0.1203
Dataset id: 2607
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the emergency withdrawal routine of a staking‑type token contract. When a user invokes the emergencyWithdraw function, the contract transfers the user's principal but fails to reset two accounting variables that track the user’s accrued bonus and the duration‑based reward multiplier (often called userCurrentBonusRatio and durationRatio). Because these variables retain their previous values, the contract’s later reward‑claim logic—executed after the protocol exits the emergency state—will calculate the user’s reward using stale ratios. This mismatch can cause the user to receive an amount that does not correspond to the actual time and bonus they have earned. The root cause is a missing state‑reset operation in the emergencyWithdraw implementation. The flaw can be exploited by a malicious participant who triggers an emergency withdrawal for themselves (or any user) and then, once the protocol is restored to normal operation, calls the claim function to pull rewards that are multiplied by the outdated bonus or duration factors. The impact is a distortion of the protocol’s accounting: users may obtain more tokens than they are entitled to, or conversely, legitimate users may receive less if the stale ratios are lower than the correct values. The issue manifests only after two conditions are met: (1) an emergency withdrawal has been performed, leaving the internal ratios unchanged, and (2) the contract is taken out of the emergency state, re‑enabling the claim function. Until the protocol exits emergency, the bug is silent because the claim path is blocked, making it hard to notice during routine testing. The affected parties include all token holders who rely on the correct calculation of rewards, the protocol’s overall tokenomics, and any downstream services that assume accurate balance reporting. The flaw was discovered during a formal security audit that reviewed state transitions in the emergency handling logic. To remediate the problem, the emergencyWithdraw function should explicitly set the user’s bonus and duration ratios to zero (or otherwise invalidate them) before completing the withdrawal, ensuring that subsequent reward calculations start from a clean state. This correction restores the intended accounting invariants and prevents reward manipulation after an emergency period.

## Proof of Concept
[HolyPaladinToken.sol#L1338](https://github.com/code-423n4/2022-03-paladin/blob/9c26ec8556298fb1dc3cf71f471aadad3a5c74a0/contracts/HolyPaladinToken.sol#L1338)

## Recommendation
Set these variables to zero in the EmergencyWithdraw function.

PR with the changes: [PaladinFinance/Paladin-Tokenomics#5](https://github.com/PaladinFinance/Paladin-Tokenomics/pull/5).  
  
Contesting the severity of the issue: even after an emergency withdraw, where the BonusRatio of the user isn’t reset back to 0, users have no way to claim extra accrued rewards, as the claim method will be blocked by the Emergency state: [HolyPaladinToken.sol#L381](https://github.com/code-423n4/2022-03-paladin/blob/9c26ec8556298fb1dc3cf71f471aadad3a5c74a0/contracts/HolyPaladinToken.sol#L381).

Given that the contract can be moved back out of the emergency state, I don’t think the sponsor’s assessment of this being a low risk issue is correct. I do think due to the external circumstances required for this to be achieved that it probably best qualifies as a medium risk.
    
`2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.`
