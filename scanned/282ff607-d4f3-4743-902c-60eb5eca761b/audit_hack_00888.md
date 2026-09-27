# [M] Compound incident: On the evening of February 23rd, UNI experienced a sudden price surge, causing Compound to fail in promptly updating UNI's price

## Summary
Severity: Medium
Target: Compound
Loss: $ 660,000
Attack method: Security Vulnerability
Published: 2024-02-23
Source: https://x.com/0xLEVI104/status/1762092203894276481
Type: slowmist-incident

## Details
On the evening of February 23rd, UNI experienced a sudden price surge, causing Compound to fail in promptly updating UNI's price. As a result, the protocol used an incorrect price provided by Uniswap's TWAP (Time-Weighted Average Price). This allowed users to borrow UNI using collateral with a lower value than UNI's actual price, leading to $660,000 in bad debt.
