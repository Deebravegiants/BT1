# [H] FEG incident: The multi-chain DeFi protocol FEG was attacked again, and the flash loan attack suffered on the BNB chain lost about $1.3 million

## Summary
Severity: High
Target: FEG
Loss: $ 1,900,000
Attack method: Flash Loan Attack
Published: 2022-05-17
Source: https://twitter.com/CertiKAlert/status/1526357878503768070
Type: slowmist-incident

## Details
The multi-chain DeFi protocol FEG was attacked again, and the flash loan attack suffered on the BNB chain lost about $1.3 million in assets. The subsequent flash loan attack on Ethereum caused a loss of about $590,000, with a total loss of about $1.9 million in assets. This attack is similar to yesterday's attack and is caused by a vulnerability in the "swapToSwap()" function. This function directly uses the "path" entered by the user as a trusted party without screening and validating the incoming parameters. Additionally, the function will allow an unverified "path" parameter (address) to use the current contract's assets. Therefore, by calling "depositInternal()" and "swapToSwap()", the attacker can obtain permission to use the assets of the current contract, thereby stealing the assets within the contract.
