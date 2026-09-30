# [C] C-2 Message Verification

## Summary
Severity: Critical
Contest weight: 0.1972
Dataset id: 7374
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A critical security vulnerability has been identified within the verify function of the ISM (Interchain Security
Module) contract. The ISM doesn't verify the caller of the Mailbox process function, which could allow
untrusted addresses to pass an arbitrary message to the Mailbox, ultimately leading to potential manipulation
of the data that will be processed.
There is also a dangerous parameter allowAll, which may lead to anyone malicious submitting oracle data if
enabled.
This issue is classified as Critical because it could lead to manipulation of critical data processed by the
process function, which could result in unpredictable disruptions or severe losses in the integrated protocols.

## Recommendation
We recommend adding caller verification of the Mailbox contract within the verify function. It should ensure
that the caller is indeed a trusted address. We also recommend removing the logic related to the allowAll
flag as it may affect the protocol security badly.
