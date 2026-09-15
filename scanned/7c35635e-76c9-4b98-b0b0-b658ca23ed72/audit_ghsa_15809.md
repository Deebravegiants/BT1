# [M] biscuit-java vulnerable to public key confusion in third party block

## Summary
Severity: Medium
Advisory: GHSA-5hcj-rwm6-xmw4
CVE: CVE-2024-41948
CWE: CWE-1259
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-5hcj-rwm6-xmw4
Type: github-advisory

## Affected
- Maven: `org.biscuitsec:biscuit` — affected >=3.0.0 <4.0.0

## Details
### Impact
Tokens with third-party blocks containing trusted annotations generated through a third party block request. Due to implementation issues in biscuit-java,  third party block support in published versions is inoperating. Nevertheless, to synchronize with other implementations, we publish this advisory and the related fix.

### Description
Third-party blocks can be generated without transferring the whole token to the third-party authority. Instead, a `ThirdPartyBlock` request can be sent, providing only the necessary info to generate a third-party block and to sign it:

the public key of the previous block (used in the signature)
the public keys part of the token symbol table (for public key interning in datalog expressions)
A third-part block request forged by a malicious user can trick the third-party authority into generating datalog trusting the wrong keypair.

Consider the following example (nominal case)
* Authority A emits the following token: `check if thirdparty("b") trusting ${pubkeyB}`
* The well-behaving holder then generates a third-party block request based on the token and sends it to third-party authority B
* Third-party B generates the following third-party block `thirdparty("b"); check if thirdparty("c") trusting ${pubkeyC}`
* The token holder now must obtain a third-party block from third party C to be able to use the token

Now, with a malicious user:
* Authority A emits the following token: `check if thirdparty("b") trusting ${pubkeyB}`
* The holder then attenuates the token with the following third party block `thirdparty("c")`, signed with a keypair pubkeyD, privkeyD) they generate
* The holder then generates a third-party block request based on this token, but alter the `ThirdPartyBlockRequest` publicKeys field and replace pubkeyD with pubkeyC
* Third-party B generates the following third-party block `thirdparty("b"); check if thirdparty("c") trusting ${pubkeyC}`
* Due to the altered symbol table, the actual meaning of the block is `thirdparty("b"); check if thirdparty("c") trusting ${pubkeyD}`
* The attacker can now use the token without obtaining a third-party block from C.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/biscuit-auth/biscuit-java/security/advisories/GHSA-5hcj-rwm6-xmw4
- https://github.com/biscuit-auth/biscuit/security/advisories/GHSA-rgqv-mwc3-c78m
- https://nvd.nist.gov/vuln/detail/CVE-2024-41948
- https://github.com/biscuit-auth/biscuit-java/commit/2e05e7b3f8f2aae38f33294f19419e2d638cb564
- https://github.com/biscuit-auth/biscuit-java
- https://github.com/biscuit-auth/biscuit-java/releases/tag/4.0.0
