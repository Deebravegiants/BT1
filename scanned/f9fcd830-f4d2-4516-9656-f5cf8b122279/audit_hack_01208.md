# [M] FTX incident: According to the X-explore blog, the hacker address starting with 0x1d37 is stealing GAS by exploiting the FTX vulnerability, mint

## Summary
Severity: Medium
Target: FTX
Loss: 81 ETH
Attack method: Contract Vulnerability
Published: 2022-10-13
Source: https://mirror.xyz/x-explore.eth/M2BJgQJaj2JK0mAO9OecByja3tU7mKXbHR_Agjs-MjA
Type: slowmist-incident

## Details
According to the X-explore blog, the hacker address starting with 0x1d37 is stealing GAS by exploiting the FTX vulnerability, minting XEN tokens 17,000 times at zero cost. The reason for this attack is that FTX does not limit the gas limit of the withdrawal transaction while the withdrawal fee is free. Instead, the estimateGas method is used to evaluate the handling fee. This method causes the GAS LIMIT to be mostly 500,000, which exceeds the default value of 21,000 by 24%. times.
