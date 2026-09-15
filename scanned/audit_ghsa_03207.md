# [H] Unauthorized access through URL manipulation

## Summary
Severity: High
Advisory: GHSA-qrmm-w4v4-q7f8
CWE: CWE-552
Ecosystem: PyPI
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-qrmm-w4v4-q7f8
Type: github-advisory

## Affected
- PyPI: `docassemble` — affected >=0 <1.2.65

## Details
### Impact
The vulnerability allows attackers to gain unauthorized access to information on the system through URL manipulation.

### Patches
The vulnerability has been patched in version 1.2.65 of the `master` branch, version 1.1.113 of the 1.1.x series, and version 1.0.12 of the `stable` branch. The Docker image on docker.io has been patched.

### Workarounds
If upgrading is not possible, manually apply the changes of https://github.com/jhpyle/docassemble/commit/e3dbf6ce054b3c0310996f0657289f5eed0a73fe and restart the server (e.g., by pressing Save on the Configuration screen).

### Credit
The vulnerability was discovered by Jim Platania of Seiso LLC (@jimmio).

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [docassemble](https://github.com/jhpyle/docassemble/issues)
* Join the [Slack channel](https://join.slack.com/t/docassemble/shared_invite/zt-ohrn8y9z-_Fb3RAl~JPBU6Km7odBPfQ)
* Email us at [jhpyle@gmail.com](mailto:jhpyle@gmail.com)

## References
- https://github.com/jhpyle/docassemble/security/advisories/GHSA-qrmm-w4v4-q7f8
