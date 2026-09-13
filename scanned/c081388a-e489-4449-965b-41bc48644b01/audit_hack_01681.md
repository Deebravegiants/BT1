# [C] TronBank incident: At 4:12 AM on May 3, Beijing time, a contract call transferred 26.73 million TRX (valued at RMB 4.27 million) from the TronBank co

## Summary
Severity: Critical
Target: TronBank
Loss: 26,730,000 TRX
Attack method: Contract Vulnerability
Published: 2019-05-03
Source: https://mp.weixin.qq.com/s/aInEaYdS9X7HP7FbzWl6AQ
Type: slowmist-incident

## Details
At 4:12 AM on May 3, Beijing time, a contract call transferred 26.73 million TRX (valued at RMB 4.27 million) from the TronBank contract, and the contract balance returned to zero. About two hours after the theft, wojak, the owner of THeRTT**, who transferred the 26.73 million TRX address, appeared. According to wojak, he wrote a script to analyze the bytecode of the TRON virtual machine, scan the contracts in batches and initiate transactions to see if there is any way to make money, but accidentally hit a bug in the Tronbank contract. At first he didn't even know that the money came from Tronbank. Some people in the community suggested that wojak return the money to the Tronbank developers, but wojak believes that this is not his problem. Developers should write test examples, do audits, and at least run some formal verifications (obviously they didn’t do anything). He is willing to return the money intact to every investor in Tronbank, not the developer of the project. Based on the available information, it is still too early to conclude that "the developer placed a backdoor in the contract". There are only two objective conclusions that can be drawn at present: 1. TRX Pro has a backdoor in the contract on the main network; 2. The code certified on TSC does not match the actual contract operation logic.
