# [M] go-witness is Vulnerable to Improper Verification of AWS EC2 Identity Documents

## Summary
Severity: Medium
Advisory: GHSA-72c7-4g63-hpw5
CVE: CVE-2025-62375
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-72c7-4g63-hpw5
Type: github-advisory

## Affected
- Go: `github.com/in-toto/go-witness` — affected >=0 <0.9.1

## Details
### Impact
This vulnerability only affects users of the AWS attestor.

Users of the AWS attestor could have unknowingly received a forged identity document. While this may seem unlikely, AWS recently issued a security bulletin about IMDS (Instance Metadata Service) impersonation.[^1]

There are multiple locations where the verification of the identity document will mistakenly report a successful verification.

- If a signature is not present or is empty
https://github.com/in-toto/go-witness/blob/0c8bb30c143951d88b1d4b32f260c5f67d30137b/attestation/aws-iid/aws-iid.go#L161-L163

- If the RSA verification of the document fails for any reason
https://github.com/in-toto/go-witness/blob/0c8bb30c143951d88b1d4b32f260c5f67d30137b/attestation/aws-iid/aws-iid.go#L192-L196

### Workarounds
The contents of the AWS attestation contain the identity document, signature, and public key that was used to verify the document. These attestations and their could be identity documents could be manually verified with the `openssl` command line as documented in the below reference from AWS.[^2]

However, the certificate containing the public key was hard-coded into the attestor. 
https://github.com/in-toto/go-witness/blob/0c8bb30c143951d88b1d4b32f260c5f67d30137b/attestation/aws-iid/aws-iid.go#L46-L66

Since the original authoring of the attestor, AWS has moved to region specific public certificates. The currently valid certificates were issued around April of 2024, making the identification of attestations with forged content difficult without additional trusted data proving the AWS region in which the attestation was created.

### Patches
This vulnerability is addressed in `go-witness` 0.9.1 and `witness` 0.10.1.

### Resources
[^1]: [AWS Security Bulletin on IMDS Impersonation](https://aws.amazon.com/security/security-bulletins/rss/aws-2025-021/)
[^2]: [Verification of instance identity documents](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/verify-iid.html#verify-signature)

## References
- https://github.com/in-toto/go-witness/security/advisories/GHSA-72c7-4g63-hpw5
- https://nvd.nist.gov/vuln/detail/CVE-2025-62375
- https://github.com/in-toto/go-witness/commit/04ff20b600e28ce8fd1aa287534dd383a1cfefb9
- https://github.com/in-toto/go-witness
