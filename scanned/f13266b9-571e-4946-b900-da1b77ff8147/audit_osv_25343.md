# [M] JavaCPP project actions vulnerable to code injection

## Summary
Severity: Medium
Advisory: CVE-2023-34112
Aliases: GHSA-36rx-hq22-jm5x
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-34112
Type: osv

## Details
JavaCPP Presets is a project providing Java distributions of native C++ libraries. All the actions in the `bytedeco/javacpp-presets` use the `github.event.head_commit.message​` parameter in an insecure way. For example, the commit message is used in a run statement - resulting in a command injection vulnerability due to string interpolation. No exploitation has been reported. This issue has been addressed in version 1.5.9. Users of JavaCPP Presets are advised to upgrade as a precaution.

## References
- https://securitylab.github.com/research/github-actions-untrusted-input/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34112.json
- https://github.com/bytedeco/javacpp-presets/security/advisories/GHSA-36rx-hq22-jm5x
- https://nvd.nist.gov/vuln/detail/CVE-2023-34112
