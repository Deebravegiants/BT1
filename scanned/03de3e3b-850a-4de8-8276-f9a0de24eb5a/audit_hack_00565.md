# [M] Port3 Network incident: The decentralized AI data network Port3 Network disclosed on X that its token PORT3 was maliciously minted by a hacker exploiting

## Summary
Severity: Medium
Target: Port3 Network
Loss: $ 830,000
Attack method: Contract Vulnerability
Published: 2025-11-23
Source: https://x.com/Port3Network/status/1992471015948210277
Type: slowmist-incident

## Details
The decentralized AI data network Port3 Network disclosed on X that its token PORT3 was maliciously minted by a hacker exploiting a cross-chain bridge vulnerability. According to on-chain analyst Yujin, the attacker used a contract flaw in the BridgeIn cross-chain bridge to mint 1 billion PORT3 tokens. The hacker then sold 162.75 million of these tokens on-chain, receiving 199.5 BNB (approximately USD 166,000) and causing the PORT3 price to plunge by 76%. Port3 Network later released an incident report explaining that the root cause stemmed from its use of NEXA Network’s CATERC20 cross-chain token solution. CATERC20 contains a boundary-condition validation vulnerability: after token ownership is renounced, a key function returns a value of 0, which unintentionally satisfies the ownership check condition. This results in permission verification failure, allowing attackers to perform privileged operations—including unauthorized token minting—without proper authorization. Notably, this issue was not identified in the CATERC20 audit report. Since Port3 had previously renounced ownership of the token to achieve greater decentralization, it remained vulnerable to this flaw. Following the incident, the Port3 team urgently removed the remaining on-chain liquidity, and several centralized exchanges suspended PORT3 deposits. Unable to continue selling, the attacker burned the remaining 837.25 million unsold PORT3 tokens approximately 40 minutes earlier.
