# [M] Lack of input checks (withrawal penalties should always be greater than 0)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-trader-joe
Published: 2022-01-27
Source: https://github.com/code-423n4/2022-01-trader-joe-findings/issues/314
Type: code-finding

## Details
# Handle

pedroais


# Vulnerability details

## Impact
If penalties are set to 0 the protocol would be vulnerable to price manipulations like the one described in the contest documentation.
## Proof of Concept
The protocol uses economic penalties to punish withdraws to protect against economic price manipulation attacks. If these penalties are set to 0 in the creation of a token launch the sale would be vulnerable to this kind of attack. The penalties should never be 0 for any token sale.

The economic attack that could be done with 0 penalties is detailed on page 7 of the whitepaper.

https://github.com/traderjoe-xyz/research/blob/main/RocketJoe_Launch_Platform_for_Bootstrapping_Protocol-Owned_Liquidity.pdf

I consider this to be a medium risk since it could completely invalidate a token launch but it's still unlikely (but possible) the creators will set penalties to 0. This could be done by mistake or by the creators of the launch event to exploit it themselves.

## Recommended Mitigation Steps
Require penalties to be greater than 0 either in the initializer function or in the factory.
