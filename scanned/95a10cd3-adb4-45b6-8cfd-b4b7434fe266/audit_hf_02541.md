# [M] Escrow cannot bridge native assets

## Summary
Severity: Medium
Contest weight: 0.0586
Dataset id: 13542
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Escrow contract has the functionality of transferring assets via Stargate after all the trading has finished. The issue with the Stargate bridging logic is that it is not able to send ETH. This is problematic on Linea as it only supports the ETH pool: https://stargateprotocol.gitbook.io/stargate/developers/pool-ids

## Recommendation
To enable sending ETH, add the ETH accumulated after trading to msg.value if the currency being bridged is native.
