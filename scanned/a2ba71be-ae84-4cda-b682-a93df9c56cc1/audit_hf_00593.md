# [H] H-01 | Possible DoS Vector In The Delegate Function

## Summary
Severity: High
Contest weight: 0.1856
Dataset id: 2091
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Delegator contract's delegate function allows users to delegate actions to a speciﬁc delegator
by updating the _delegators mapping. However, this function lacks proper access control
mechanisms, permitting any user to overwrite existing delegations for any delegator address.
Consequently, an attacker can call delegate with a target delegator address and replace the
legitimate owner and action count with arbitrary values.
This vulnerability enables a DoS attack, where the original delegator is obstructed from performing
delegated actions because their delegation has been maliciously overwritten.

## Recommendation
Update the delegate function so it can only be called if the _delegators[delegator].owner is equal to
the address(0). Implement a new removeDelegate function that allows the delegator to reset the
_delegators[delegator] mapping.
This way, the delegator can accept new delegations as now _delegators[delegator].owner is equal to
the address(0).
