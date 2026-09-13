# [C] Balancer V2 incident: The DeFi protocol Balancer V2 suffered a vulnerability exploit that affected its Composable Stable Pools. The root cause of the in

## Summary
Severity: Critical
Target: Balancer V2
Loss: $ 121,100,000
Attack method: Business Logic Flaw
Published: 2025-11-03
Source: https://x.com/balancer/status/1990856260988670132
Type: slowmist-incident

## Details
The DeFi protocol Balancer V2 suffered a vulnerability exploit that affected its Composable Stable Pools. The root cause of the incident was an incorrect rounding direction in the Stable Pool’s “exact-out” swap path. This flaw was amplified under conditions of precision errors introduced by rate providers and extremely low liquidity, allowing the attacker to manipulate the invariant and distort the BPT price calculation. As a result, the attacker was able to withdraw large amounts of assets from the pool at a cost far below their real value.The attack caused a total loss of $121.1 million across Ethereum, Arbitrum, Base, Optimism, and Polygon. As of November 19, coordinated mitigation efforts enabled several security measures to be deployed promptly after the issue was discovered, resulting in approximately $45.7 million in user funds being protected or recovered.
