# [M] Custom sAVAX Aave Rebalancer contract incident: A custom sAVAX Aave Rebalancer contract on Avalanche was exploited. The public function b2a13230() allowed the caller to pass arbi

## Summary
Severity: Medium
Target: Custom sAVAX Aave Rebalancer contract
Loss: $ 64,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-19
Source: https://telemetr.io/uz/channels/2360854548-defimon_alerts
Type: slowmist-incident

## Details
A custom sAVAX Aave Rebalancer contract on Avalanche was exploited. The public function b2a13230() allowed the caller to pass arbitrary target and data, executing target.call(data) while the contract still held the user’s Aave V3 Credit Delegation (borrowing permission). The attacker used this to call Aave’s borrow() on behalf of the victim and drain WAVAX. A whitehat bot frontran the transaction and recovered all funds before any withdrawal, resulting in zero net loss to the user.
