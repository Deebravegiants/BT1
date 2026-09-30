# [H] Dca order executor can grief order user

## Summary
Severity: High
Reporter: evilakela
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237
Type: audit-issue

## Details
# Dca order executor can grief order user

## Summary
`Dca.execute_dca_order` executor can choose any path and any fee as long as it actually swaps token in to token out. Thus bad executor can choose bad path and fees. 

## Vulnerability Detail
For example attacker could create pools with his own token and execute trade through it: token in => BAD_TOKEN => token out with max fees. Or just use existing pools with max fees. Note: slippage protection doesn't protect from high fee.

## Impact
User suffer bad trade due to high fee.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165-L237

## Tool used
Manual Review

## Recommendation
I would recommend at least give user an option to allow only protocol keepers to execute his order.
