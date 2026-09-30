# [M] M-07 | OracleBonds Address Change Mishandles Funds

## Summary
Severity: Medium
Contest weight: 0.1310
Dataset id: 2299
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setOracleBonds function in the TruthMarketManager contract allows the owner to change the
oracleBonds address. The problem is that the oracleBonds address is hardcoded into markets when
they are created.
If the address is updated in the TruthMarketManager contract, active markets not yet finalized will
send and account for resolve, dispute, and escalate bonds to the new address.
However, when issuing them back, the old address in the market contract will be used, which will not
have the funds or have them accounted for, leading to users losing those funds.
Furthermore, any unclaimed dispute bonds will also be unclaimable because the OracleCouncil
contract will fetch the new address from the TruthMarketManager contract, while these dispute
bonds are stored in and accounted for in the old contract.

## Recommendation
If an oracleBonds update is needed, ensure it is performed only when all active markets are finalized
and manually handle users' unclaimed disputed bonds, as the normal functionality will not work for
pending disputes before the address change.
