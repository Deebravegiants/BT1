# [M] YIEDL incident: According to intelligence from the SlowMist Security Team, the YIEDL project on the BSC chain was attacked, with the attacker stea

## Summary
Severity: Medium
Target: YIEDL
Loss: $ 300,000
Attack method: Contract Vulnerability
Published: 2024-04-25
Source: https://twitter.com/SlowMist_Team/status/1782962346039898473
Type: slowmist-incident

## Details
According to intelligence from the SlowMist Security Team, the YIEDL project on the BSC chain was attacked, with the attacker stealing approximately $300,000. In this incident, the reason lies in the contract’s failure to adequately validate the external parameter(dataList) provided by the user during the processing of the redeem function call. This parameter is critical data for controlling asset exchanges, typically containing specific transaction instructions or routing information. The attacker maliciously constructed this external parameter, enabling unauthorized asset transfers.
