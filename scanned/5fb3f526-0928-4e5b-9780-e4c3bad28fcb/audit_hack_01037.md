# [M] APEDAO incident: APEDAO on the BNB chain was attacked and the loss was approximately $7,000. The attacker transferred APEDAO to the pair contract

## Summary
Severity: Medium
Target: APEDAO
Loss: $ 7,000
Attack method: Contract Vulnerability
Published: 2023-07-18
Source: https://twitter.com/BeosinAlert/status/1681316257034035201
Type: slowmist-incident

## Details
APEDAO on the BNB chain was attacked and the loss was approximately $7,000. The attacker transferred APEDAO to the pair contract. The APEDAO contract mistook the attacker's behavior as a selling operation and gradually accumulated a value named "amountToDead". The attacker repeatedly transferred APEDAO and then used the skim function to withdraw excess tokens. Eventually, the attacker calls the godead function to destroy APEDAO held in the pairing contract, causing the token price to rise.
