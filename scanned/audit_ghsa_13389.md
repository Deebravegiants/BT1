# [M] Ineffective privileges drop when requesting container network

## Summary
Severity: Medium
Advisory: GHSA-mmx5-32m4-wxvx
CVE: CVE-2023-38496
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-mmx5-32m4-wxvx
Type: github-advisory

## Affected
- Go: `github.com/apptainer/apptainer` — affected >=1.2.0 <1.2.1

## Details
### Impact

Fix https://github.com/apptainer/apptainer/pull/1523 included in Apptainer 1.2.0-rc.2 has introduced an ineffective privilege drop when requesting container network setup, therefore subsequent functions are called with root privileges.  The attack surface is rather limited for users but an attacker could possibly craft a starter config to delete any directory on the host filesystems.  Only affects setuid installations of Apptainer.  

### Patches

The security fix https://github.com/apptainer/apptainer/pull/1578 has been included in Apptainer 1.2.1

### Workarounds

There is no known workaround outside of upgrading to Apptainer 1.2.1

## References
- https://github.com/apptainer/apptainer/security/advisories/GHSA-mmx5-32m4-wxvx
- https://nvd.nist.gov/vuln/detail/CVE-2023-38496
- https://github.com/apptainer/apptainer/pull/1523
- https://github.com/apptainer/apptainer/pull/1578
- https://github.com/apptainer/apptainer
