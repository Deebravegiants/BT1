# [M] Signature replay

## Summary
Severity: Medium
Contest weight: 0.4669
Dataset id: 1420
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a signature replay flaw in the PoolTemplate contract that allows an attacker to reuse an insurance claim in order to extract additional funds from the pool. The root cause is insufficient validation of the incident timestamp and the insurance span parameters. When the contract’s applyCover function creates an incident, it does not verify that the provided _incidentTimestamp is earlier than the current block timestamp, nor does the insure method enforce that the _span argument is greater than zero. Consequently, a malicious owner can publish an incident with a future timestamp, and an attacker can call insure with a large amount, receiving a Merkle‑based proof that only includes the target and insured addresses. Because the incident’s timestamp is not part of the proof, the same insurance data can be presented again after the future timestamp becomes current, enabling a replay of the claim. The replay can be repeated as long as the incident remains in effect, effectively draining pool assets or causing multiple payouts for a single insured event. This condition occurs whenever the contract relies solely on the Merkle proof of target and insured and no additional time‑bound checks are performed, which is typical for insurance‑type protocols that expect incidents to be created only with past timestamps. The affected parties include any user who purchases insurance, the pool’s liquidity providers, and the protocol itself, as its assets may be siphoned without proper compensation. The issue was uncovered during a Code4rena audit, where the auditors identified that the incident creation logic does not protect against future timestamps and that the span validation is missing. The flaw can be hard to notice because the Merkle verification appears to succeed, and no explicit error is thrown when the timestamp is in the future; the contract’s UI may simply show that a claim is pending, while in reality the claim can be replayed later. To remediate the issue, the contract should enforce that _incidentTimestamp < block.timestamp when an incident is created, and that _span is strictly greater than zero (or meets a minimum duration). Additionally, the incident timestamp and span should be incorporated into the data covered by the Merkle proof so that any replay attempt would fail verification. By tightening these checks, the protocol can ensure that each insurance claim is bound to a single, time‑restricted incident, preserving the intended accounting and preventing funds from disappearing due to replay attacks.

## Proof of Concept
The `redeem` method of `PoolTemplate` verifies the data stored in `incident`, and the verification logic of this process is performed as following:
    
```solidity
require(
    MerkleProof.verify(
        _merkleProof,
        _targets,
        keccak256(
            abi.encodePacked(_insurance.target, _insurance.insured)
        )
    ) ||
        MerkleProof.verify(
            _merkleProof,
            _targets,
            keccak256(abi.encodePacked(_insurance.target, address(0)))
        ),
    "ERROR: INSURANCE_EXEMPTED"
);
```
As can be seen, the only data related to the `_insurance` are`target` and `insured`, so as the incident has no relation with the`Insurance`, apparently nothing prevents a user to call `insure` with high amounts, after receive the incident, the only thing that prevents this from being reused is that the owner creates the incident with an `_incidentTimestamp` from the past.

So if an owner create a incident from the future it’s possible to create a new `insure` that could be reused by the same affected address.

Another lack of input verification that could facilitate this attack is the `_span=0` in the `insure` method.

## Recommendation
It is mandatory to add a check in `applyCover` that`_incidentTimestamp` is less than the current date and the `span` argument is greater than 0 in the`insure` method.
agree on the _incidentTimestamp check. disagree on span check since there already is
     
     
     require(
                 parameters.getMinDate(msg.sender) <= _span,
                 "ERROR: INSURE_SPAN_BELOW_MIN"
             );
 
we are going to set default value of 1week for everyone

we assume ownership control works fine. this can lose money in-proper way, but not at risk since onlyOwner modifier applied.

going to leave this as 2 
 
`2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.`
 
The external requirement here would be an incorrect timestamp from the owner which would cause assets to be at risk from the replay. 

there is
     
     
     _span >= getMinDate() 
     
so we don’t implement _span > 0
