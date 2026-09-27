# [M] jwcrypto token substitution can lead to authentication bypass

## Summary
Severity: Medium
Advisory: GHSA-gwp4-mcv4-w95j
CVE: CVE-2022-3102
Ecosystem: PyPI
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-gwp4-mcv4-w95j
Type: github-advisory

## Affected
- PyPI: `jwcrypto` — affected >=0 <1.4

## Details
The JWT code can auto-detect the type of token being provided, and this can lead the application to incorrect conclusions about the trustworthiness of the token.
Quoting the private disclosure we received : "Under certain circumstances, it is possible to substitute a [..] signed JWS with a JWE that is encrypted with the public key that is normally used for signature validation."
This substitution attack can occur only if the validating application also have access to the private key, normally used to sign the tokens, available during validation of the received JWT.
The significance of this attacks depends on the use of the token, it may lead to authentication bypass or authorization bypass (respectively if claims are used to authenticate or authorize certain actions), because the attacker has full control of the data placed in the JWE and can inject any desired claim value.

Several mitigating factors exist that can protect applications from this issue:
- If the private key corresponding to the public key used to encrypt the JWE is not available to the application an exception will be raised.
- If the JWK is specified with the 'use' parameter set to 'sig' (as expected for keys used only for signing/verification) an exception will be raised.
- If the JWK is specified with the 'key_ops' parameter set and it does not include the 'decrypt' operation an exception will be raised.
- Applications may check the token type before validation, in this case they would fail to detect an expected JWS

Normally, signing and validation are done by different applications, so this scenario should be unlikely. However it is possible to have applications that both sign and validate tokens and do not separate JWKs in use, or do not set a JWK 'use' type.

Due to the mitigating factors, and the fact that specific operational constraints and conditions need to be in place to successfully exploit this issue to generate an authentication bypass, we rate this security issue as moderate. Other avenues may decide on a different rating based on use case, always verify what conditions apply to your use of the library to assess risk.

Many thanks to Tom Tervoort of Secura for finding and reporting this issue.

## References
- https://github.com/latchset/jwcrypto/security/advisories/GHSA-gwp4-mcv4-w95j
- https://github.com/latchset/jwcrypto/commit/f4e912f83cb578e2cd47f8a9398bf15f680bf558
- https://github.com/latchset/jwcrypto
- https://github.com/latchset/jwcrypto/releases/tag/v1.4.0
