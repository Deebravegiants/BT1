# [M] debug_forceReceiveMessage is dangerous and could be abused

## Summary
Severity: Medium
Contest weight: 0.0828
Dataset id: 6184
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The debug_forceReceiveMessage function in LayerZeroAdapter is a restricted function that allows privileged actors to deliver arbitrary messages to the Bridge contract. For example, a privileged actor could deliver a random payload to the Bridge contract without sending it through LayerZero. This ability could lead to stealing NFTs from the Bridge contract and minting them without constraints. This also undermines the security offered by LayerZero as a cross-chain communication protocol.

## Recommendation
Consider removing the debug_forceReceiveMessage function. Sweep n' Flip: Fixed in snf-bridge-contracts-v1 PR 15.
