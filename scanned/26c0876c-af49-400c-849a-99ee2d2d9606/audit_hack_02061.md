# [M] 6.2 Missing Slippage Protection for Users

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Partially Corrected Acknowledged

There is no slippage protection for users interacting with the mint(), burn(), deposit() or
withdraw() functions of a StableMaster contract nor for actors interacting with certain functions of a
PerpetualManager contract which calculate the cash out amount of a perpetual.

A user can get caught unlucky, especially as fees depend on the current state of the system or as the
cash out amount of a perpetual depends on the current rate returned by the Oracle. There is a risk of
sandwich attacks on user's transaction: A user's transaction may be sandwiched between two of the
attacker's transaction. The first transaction of the attacker may change the state of a system resulting in
an unfavorable outcome of the user's transaction while the attacker profits with his second transaction
just after the user's transaction.

Code partially corrected:

A slippage protection has been added for stable seekers minting and burning. Slippage protection has
been introduced for hedging agents.

Acknowledged:

However, it was concluded that not further slippage protection for standard liquidity providers is
necessary.
