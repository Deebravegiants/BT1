# [M] wxBTRFLY incident: White hat hackers at @immunefi discovered a critical vulnerability in the wxBTRFLY Token contract. The transferFrom function in th

## Summary
Severity: Medium
Target: wxBTRFLY
Loss: -
Attack method: Contract Vulnerability
Published: 2022-01-16
Source: https://twitter.com/redactedcartel/status/1482497468713611266?s=20
Type: slowmist-incident

## Details
White hat hackers at @immunefi discovered a critical vulnerability in the wxBTRFLY Token contract. The transferFrom function in the contract did not update the recipient's authorization correctly, and would incorrectly update the msg.sender's authorization. Although the vulnerability itself is serious, the cause is not complicated (more like a clerical error produced by the developer). What is more interesting is the official repair method. Since the contract itself does not support upgrade, the contract code cannot be updated directly; the contract does not support suspension, so it is not possible to transfer user assets by means of snapshot + migration. The final official measure was to launch an attack transaction by itself, transferring the assets of all users affected by the vulnerability to a multi-signature wallet.
