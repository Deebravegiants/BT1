# [M] Polygon zkEVM incident: Blockchain security researcher iczc tweeted that a vulnerability was found in Polygon zkEVM and received a bug bounty from Immunef

## Summary
Severity: Medium
Target: Polygon zkEVM
Loss: -
Attack method: Logic Vulnerability
Published: 2023-05-29
Source: https://twitter.com/0xiczc/status/1662090451493740545
Type: slowmist-incident

## Details
Blockchain security researcher iczc tweeted that a vulnerability was found in Polygon zkEVM and received a bug bounty from Immunefi L2. The vulnerability prevents asset migration from L1 to L2 by preventing assets bridged from L1 to Polygon zkEVM (L2) from being properly claimed in L2. iczc found in the code logic of processing claim tx pre-execution results that malicious attackers can bypass the "isReverted" pre-execution check on claim transactions by setting the gas fee to non-zero, allowing them to send a large number of Low-cost claims DoS attacks on sequencers and validators, increasing computational overhead. Also, transactions are not immediately removed from the pool after execution. The status is updated from Pending to Selected and continues to exist in the PostgreSQL database. Currently, there is only one trusted sequencer capable of fetching transactions from the transaction pool and executing them. Therefore, another vulnerability is to maliciously mark any deposit amount by sending a failed transaction. This will cause claim transactions that correctly use credits to be rejected because the credits are already used. This makes the L2 network unusable for new users. The Polygon zkEVM team fixed this vulnerability by removing the specific gas logic for claiming transactions, with no funds at risk.
