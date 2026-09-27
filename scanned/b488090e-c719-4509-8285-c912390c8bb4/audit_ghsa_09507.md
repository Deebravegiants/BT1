# [H] awslabs/tough is Missing Delegated Metadata Validation

## Summary
Severity: High
Advisory: GHSA-4v58-8p28-2rq3
CVE: CVE-2026-6967
CWE: CWE-345
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-4v58-8p28-2rq3
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0.9.0 <0.22.0
- crates.io: `tuftool` — affected >=0 <0.15.0

## Details
### Summary
Missing expiration, hash, and length enforcement in delegated metadata validation in awslabs/tough before tough-v0.22.0 allows remote authenticated users with delegated signing authority to bypass TUF specification integrity checks for delegated targets metadata and poison the local metadata cache, because load_delegations does not apply the same validation checks as the top-level targets metadata path.

### Impact
The tough library, prior to 0.22.0, does not properly verify delegated target metadata. It allows someone with write access to the metadata to serve expired or otherwise invalid targets from a TUF repository which tough will then trust rather than reject.

### Impacted Versions: 
tough 0.9.0 through 0.21.x, tuftool through 0.14.x

### Patches
This issue has been addressed in tough version 0.22.0 and tuftool version 0.15.0. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

### Workarounds
No workarounds to this issue are known.

### References
* CVE-2026-6967
If there are any questions or comments about this advisory, please contact [AWS/Amazon] Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement

Amazon Web Services Labs would like to thank Oleh Konko of 1seal for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/awslabs/tough/security/advisories/GHSA-4v58-8p28-2rq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-6967
- https://aws.amazon.com/security/security-bulletins/2026-019-aws
- https://crates.io/crates/tough/0.22.0
- https://crates.io/crates/tuftool/0.15.0
- https://github.com/awslabs/tough
- https://github.com/awslabs/tough/releases/tag/tough-v0.22.0
- https://github.com/awslabs/tough/releases/tag/tuftool-v0.15.0
