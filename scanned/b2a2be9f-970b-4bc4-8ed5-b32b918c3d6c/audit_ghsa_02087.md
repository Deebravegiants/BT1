# [M] Asymmetric Resource Consumption (Amplification) in Docker containers created by Wings 

## Summary
Severity: Medium
Advisory: GHSA-jj6m-r8jc-2gp7
CVE: CVE-2021-32699
CWE: CWE-405, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-jj6m-r8jc-2gp7
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.4.4

## Details
### Impact
All versions of Pterodactyl Wings preior to `1.4.4` are vulnerable to system resource exhaustion due to improper container process limits being defined. A malicious user can consume more resources than intended and cause downstream impacts to other clients on the same hardware, eventually causing the physical server to stop responding.

### Patches
Users should upgrade to `1.4.4`.

### Workarounds
There is no non-code based workaround for impacted versions of the software. Users running customized versions of this software can manually set a PID limit for containers created.

### For more information
If you have any questions or comments about this advisory:
* Contact us on [Discord](https://discord.gg/pterodactyl)
* Email us at `dane ät pterodactyl dot io`

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-jj6m-r8jc-2gp7
- https://nvd.nist.gov/vuln/detail/CVE-2021-32699
- https://github.com/pterodactyl/wings/commit/e0078eee0a71d61573a94c75e6efcad069d78de3
- https://github.com/pterodactyl/wings
