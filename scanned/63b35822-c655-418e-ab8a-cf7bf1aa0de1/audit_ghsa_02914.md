# [H] Signature verification vulnerability in Stark Bank ecdsa libraries

## Summary
Severity: High
Advisory: GHSA-9wx7-jrvc-28mm
CWE: CWE-347
Ecosystem: Maven, NuGet, PyPI, npm
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-9wx7-jrvc-28mm
Type: github-advisory

## Affected
- PyPI: `starkbank-ecdsa` — affected >=0 <2.0.1
- Maven: `com.starkbank:ecdsa-java` — affected >=1.0.0 <1.0.1
- NuGet: `starkbank-ecdsa` — affected >=1.3.1 <1.3.2
- npm: `starkbank-ecdsa` — affected >=1.1.2 <1.1.3

## Details
An attacker can forge signatures on arbitrary messages that will verify for any public key. This may allow attackers to authenticate as any user within the Stark Bank platform, and bypass signature verification needed to perform operations on the platform, such as send payments and transfer funds. Additionally, the ability for attackers to forge signatures may impact other users and projects using these libraries in different and unforeseen ways.

## References
- https://github.com/starkbank/ecdsa-python/commit/d136170666e9510eb63c2572551805807bd4c17f
- https://github.com/starkbank/ecdsa-dotnet
- https://github.com/starkbank/ecdsa-java
- https://github.com/starkbank/ecdsa-node
- https://github.com/starkbank/ecdsa-python
- https://github.com/starkbank/ecdsa-python/compare/v2.0.0...v2.0.1
- https://github.com/starkbank/ecdsa-python/releases/tag/v2.0.1
- https://research.nccgroup.com/2021/11/08/technical-advisory-arbitrary-signature-forgery-in-stark-bank-ecdsa-libraries
