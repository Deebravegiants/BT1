# [M] Incorrect TOKEN_ADDRESS and DSR_DEPOSIT_ADDRESS

## Summary
Severity: Medium
Contest weight: 0.1034
Dataset id: 10753
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DSRStrategy declares incorrect contract addresses for TOKEN_ADDRESS and
DSR_DEPOSIT_ADDRESS, which are intended to represent the sDAI contract for
depositing DAI tokens and earning yield.
//mainnet
address public constant TOKEN_ADDRESS = 0x3F1c547b21f65e10480dE3ad8E19fAAC46C95034;
address public constant DSR_DEPOSIT_ADDRESS = 0x3F1c547b21f65e10480dE3ad8E19fAAC46C95034;
The DSRStrategy is primarily used as the implementation strategy for the
DepositUSD contract on the Ethereum mainnet. However, the current
addresses point to an account with no code.
This will prevent all operations and interactions with the intended address.

## Recommendation
Update the TOKEN_ADDRESS and DSR_DEPOSIT_ADDRESS to the correct address:
sDAI: 0x83F20F44975D03b1b09e64809B757c47f942BEeA (ETH Mainnet).
