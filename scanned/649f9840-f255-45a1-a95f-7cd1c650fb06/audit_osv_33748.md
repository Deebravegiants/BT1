# [H] Conjur OSS and Secrets Manager, Self-Hosted (formerly Conjur Enterprise) Vulnerable to Bypass of IAM Authenticator

## Summary
Severity: High
Advisory: CVE-2025-49827
Aliases: GHSA-gmc5-9mpc-xg75
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2025-49827
Type: osv

## Details
Conjur provides secrets management and application identity for infrastructure. Conjur OSS versions 1.19.5 through 1.22.0 and Secrets Manager, Self-Hosted (formerly known as Conjur Enterprise) 13.1 through 13.5 and 13.6 are vulnerable to bypass of the IAM authenticator. An attacker who can manipulate the headers signed by AWS can take advantage of a malformed regular expression to redirect the authentication validation request that Secrets Manager, Self-Hosted sends to AWS to a malicious server controlled by the attacker. This redirection could result in a bypass of the Secrets Manager, Self-Hosted IAM Authenticator, granting the attacker the permissions granted to the client whose request was manipulated. This issue affects both Secrets Manager, Self-Hosted (formerly Conjur Enterprise) and Conjur OSS. Conjur OSS version 1.22.1 and Secrets Manager, Self-Hosted versions 13.5.1 and 13.6.1 fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/07/16/7
- http://www.openwall.com/lists/oss-security/2025/08/08/1
- https://github.com/cyberark/conjur/releases/tag/v1.22.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49827.json
- https://github.com/cyberark/conjur/security/advisories/GHSA-gmc5-9mpc-xg75
- https://nvd.nist.gov/vuln/detail/CVE-2025-49827
