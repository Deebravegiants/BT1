# [H] Sponsorship front-running

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

If proposal submission and sponsorship are done in 2 different transactions, it's possible to front-run the `sponsorProposal` function by any member. The incentive to do that is to be able to block the proposal afterwards. It's sometimes possible to block the proposal by getting blacklisted at `depositToken`. In that case, the proposal won't be accepted and the emergency processing is going to happen next. Currently, if the attacker can become whitelisted again, he might even not lose the deposit tokens. If not, it will block the whole system forever and everyone would have to ragequit (but that's the part of another issue).

#### Recommendation

Pull pattern for token transfers will solve the issue. Front-running will still be possible but it doesn't affect anything.
