# [H] Late-depositors can claim value intended for earlier depositors

## Summary
Severity: High
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#LL222C10-L222C21
Type: audit-issue

## Details
# Late-depositors can claim value intended for earlier depositors

## Summary

amount_claimable_per_share is set based on the total_shares at the time. Anyone depositing at a point after the first call to withdraw_underlying_to_claim will be able to claim value intended for previous depositors.

## Vulnerability Detail

withdraw_underlying_to_claim updates amount_claimable_per_share based on the current value of total_shares

register_deposit increases the number of shares, with no time limit on it being called

claim() lets a user claim  `position.shares_owned * amount_claimable_per_share` tokens.

Putting these together, someone who gets a deposit registered after someone called withdraw_underlying_to_claim can get everyone else's tokens.

Note that the contest rules say:

* During the auction phase all priviledged roles have to be trusted.
* Migration admin has to be trusted for the entire time, as long as there is an active position.
* Alchemix admins, protocol and underlying tokens have to be trusted.


However, nothing says depositors must be trusted after the auction phase.

Further, even if deposits may only occur through the auction house, there is another attack that allows deposits to be made arbitrarily late by abusing the anti-sniping mechanism. See https://github.com/sherlock-audit/2023-02-fair-funding-jkoppel/issues/6

## Impact

Late depositors can claim more than their initial deposit.

Someone who makes a sufficiently-late deposit equal to the sum of all other positions will be able to claim 100% of everyone else's deposits.

## Code Snippet

register_deposit increases number of shares, with no limit on it being called arbitrarily late: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#LL222C10-L222C21

mark_as_claimable uses current value of total_shares to compute amount_claimable_per_share: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L419

Computation of amount claimable, based only on amount_claimable_per_share and number of shares: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L439

## Tool used

Manual Review

## Recommendation

Make the Vault  have two distinct states, with transition controlled by the operator. In the initial state, deposits may be made, but no withdraws may be performed. In the closed state, no deposits may be made, but withdrawals may be performed.
