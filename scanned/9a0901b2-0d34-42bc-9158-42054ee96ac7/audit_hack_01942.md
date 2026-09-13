# [H] 6.1 Oracle Manipulation

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

To prevent manipulation, Bancor v3 calculates a moving average of each pool's spot price that is
adjusted once per block. Critical actions like the increase of trading liquidity or withdrawal of funds


requires the spot rate of a pool to not diverge from this moving average by more than a certain
percentage.

Since the moving average is calculated as an arithmetic mean, it is subject to manipulation. Consider the
following scenario:

- An attacker funds a pool with some tokens with a spot rate of 1 BNT : 1 token.
- They perform a trade from BNT to the token by providing an amount of BNT that changes the spot
    rate to 10 BNT : 1 token. The average rate is now 2.8 BNT : 1 token.
- In the next block, they perform another trade from token to BNT to bring the spot rate back to 2.
    BNT : 1 token.
- Since the spot rate now equals the average rate, the attacker can withdraw his supplied tokens.
- The pool does not contain enough tokens to satisfy the withdrawal, so the attacker gets
    compensated in BNT for the outstanding amount.
- This compensation is calculated with the average rate of the pool which now is 2.8 BNT to 1 token
    instead of the real 1 : 1 rate.
- The attacker will receive 2.8 times the amount of BNT he is actually eligible to receive.

The attacker is required to split both trades in 2 consecutive blocks. In the first block, they create an
arbitrage opportunity that can be utilized by an arbitrageur. To make sure, their initial investment will not
be lost, they must selfishly mine 2 blocks in a row. This is possible with around 1.5% of the total hashrate
of Ethereum. Renting this amount of hashrate is in the realm of possibilities and we estimate that the cost
of renting the hashrate and losing out on the reward of the additional mined blocks results in a total cost
of ~150.000 USD.

Alternatively, an attacker could try to spam transactions to the Ethereum network in order for their second
transaction to be executed before the transactions of any arbitrage bot.

Furthermore, after Ethereum's transition to Proof-of-Stake, the attack becomes simpler: As the attacker
now knows when it is their turn for validation, they could submit their first transaction right to the block
before. Using Flashbots, the transaction could actually be hidden so that no arbitrage bots would see it
before it is included in the block. The next block is then in the hand of the attacker.

While this attack is hard to carry out and requires a lot of capital, it can also create immense losses.

Code corrected:

A second moving average for the inverse rate has been introduced. Averages for the rate and the inverse
rate are calculated independently which prevents the aforementioned attack. The resulting inverse rate in
the example would diverge from the inverse spot rate by ~100%.
