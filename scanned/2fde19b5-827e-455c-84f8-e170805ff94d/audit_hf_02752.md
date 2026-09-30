# [C] No Duplication Checks For Peg-In Proofs

## Summary
Severity: Critical
Contest weight: 0.1322
Dataset id: 15107
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A single call to mint() can contain multiple peg-in proofs, this is required when a user performs peg-in transactions within a single bitcoin block. However, no duplication checks occur for these proofs. As such, an attacker can duplicate a valid proof and submit them to mint() to multiply their received amount. The impact and likelihood are high as it allows any user to replay a peg-in an arbitrary amount of times to mint BTC to their Botanix address.

## Recommendation
Implement duplication checks or more granular replay protection for peg-in validation.
