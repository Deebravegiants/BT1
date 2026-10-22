# [M] Profile creation can be frontrun

## Summary
Severity: Medium
Contest weight: 0.1616
Dataset id: 1526
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[PublishingLogic.sol#L50](https://github.com/code-423n4/2022-02-aave-lens/blob/aaf6c116345f3647e11a35010f28e3b90e7b4862/contracts/libraries/PublishingLogic.sol#L50)  

The `LensHub/PublishingLogic.createProfile` function can be frontrun by other whitelisted profile creators.  
An attacker can observe pending `createProfile` transactions and frontrun them, own that handle, and demand ransom from the original transaction creator.

## Recommendation
Everyone needs to use flashbots / private transactions but it might not be available on the deployed chain.  
A commit/reveal scheme for the handle and the entire profile creation could mitigate this issue.

Declined. This is by design. Governance can allow contracts/addresses to mint. If governance allows a malicious actor that is the fault of governance. Governance can also allow contracts that implement auction/commit reveal or other functionality as well to manage the profile minting system.
The protocol should take no opinion on this by default.

While I agree that this is the fault of the governance, I think it still stands that any whitelisted user may be compromised or become malicious at a later point in time. For that reason, I think this issue has some validity although due to the unlikely nature (requiring a faulty governance), I’ll mark this as `medium` risk for now.

I disagree on the medium risk. Governance being faulty is not enough of a reason IMO. Like most governance-included protocols, governance getting compromised bears risks that are largely unavoidable.

While I agree that a faulty governance is an extremely unlikely outcome. It isn’t stated in the README and as per the judges’ guidelines, profiles can be front-run under specific stated assumptions/external requirements. A malicious whitelisted profile creator can reasonably front-run other creators. 
`2 — Med (M): vulns have a risk of 2 and are considered “Medium” severity when assets are not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.`

Fair enough, though we were aware of this— it’s clear it falls into a medium severity. We’re acknowledging this!
