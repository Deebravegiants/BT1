# [C] Invalid Peg-in Proofs May Drain The Minting Contract

## Summary
Severity: Critical
Contest weight: 0.2732
Dataset id: 15108
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In execute_state_transitions(), if the validation of a peg-in proof fails, the balance of the receiver is decremented with the amount they originally received. However, this does not take into account that this amount is then eﬀectively removed from the minting contract and taken out of the total supply. This allows for an attack where a user calls mint() with an invalid proof and amount set to the minting contract’s entire balance. The minting contract then transfers its entire balance to the user, afterwards, the proof is checked and found invalid such that the users balance is decremented again. However, the minting contract is not refunded this balance. The impact and likelihood of the issue are rated as high as any attacker may cause a permanent denial of service of the peg-in mechanism, since the contract no longer has any balance to pay out to other minters. The inverse of this issue occurs in burn(), where if a burn() is invalid the burner is refunded the value without it being taken out of the minting contract's balance.

## Recommendation
A mitigation to the issue is to only mint tokens to the user after the proof has been veriﬁed. This may be implemented by performing balance modiﬁcations during peg-in validation in execute.rs. As a result, if the proof is invalid, the minting contract does not lose any balance. For the burn() function, user tokens must be consumed during the smart contract call to avoid double spending. Therefore, the resolution would be to update the Minting contract balance if a user is refunded during peg-out validation.
