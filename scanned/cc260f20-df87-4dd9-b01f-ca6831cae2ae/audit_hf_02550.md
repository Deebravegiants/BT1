# [M] Integration with Curve is flawed

## Summary
Severity: Medium
Contest weight: 0.0614
Dataset id: 13559
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, the Curve methods deposit and withdraw are hardcoding the number of underlying tokens in a Curve pool to be exactly two. This is incorrect, as some pools have three or more underlying tokens and with the current implementations users can't make proxy calls to them, which limits the functionality of the protocol.

## Recommendation
Change the methods in Curve so that they can work for different counts of underlying tokens in a pool, make sure to do this with a proper validations.
