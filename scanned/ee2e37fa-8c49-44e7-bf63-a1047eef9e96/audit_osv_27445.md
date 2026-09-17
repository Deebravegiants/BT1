# [C] Arbitrary Expression Injection in github workflow leads to Command execution & leaking secrets

## Summary
Severity: Critical
Advisory: CVE-2024-21623
Aliases: GHSA-q6gr-wc79-v589
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2024-21623
Type: osv

## Details
OTCLient is an alternative tibia client for otserv. Prior to commit db560de0b56476c87a2f967466407939196dd254, the /mehah/otclient "`Analysis - SonarCloud`" workflow is vulnerable to an expression injection in Actions, allowing an attacker to run commands remotely on the runner, leak secrets, and alter the repository using this workflow. Commit db560de0b56476c87a2f967466407939196dd254 contains a fix for this issue.

## References
- https://github.com/mehah/otclient/blob/72744edc3b9913b920e0fd12e929604f682fda75/.github/workflows/analysis-sonarcloud.yml#L91-L104
- https://securitylab.github.com/research/github-actions-preventing-pwn-requests/
- https://securitylab.github.com/research/github-actions-untrusted-input/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21623.json
- https://github.com/mehah/otclient/security/advisories/GHSA-q6gr-wc79-v589
- https://nvd.nist.gov/vuln/detail/CVE-2024-21623
- https://github.com/mehah/otclient/commit/db560de0b56476c87a2f967466407939196dd254
