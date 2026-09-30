# [M] Function `cooldown

## Summary
Severity: Medium
Contest weight: 0.0765
Dataset id: 2609
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[HolyPaladinToken.sol#L228-L235](https://github.com/code-423n4/2022-03-paladin/blob/9c26ec8556298fb1dc3cf71f471aadad3a5c74a0/contracts/HolyPaladinToken.sol#L228-L235)  

Function cooldown() is not protected when protocol is in emergency mode.  
Its behavior is not consistent with the other major functions defined.

## Recommendation
Add checking for emergency mode for this function also.
    
    if(emergency) revert EmergencyBlock();

Changes made in: [PaladinFinance/Paladin-Tokenomics#10](https://github.com/PaladinFinance/Paladin-Tokenomics/pull/10).
