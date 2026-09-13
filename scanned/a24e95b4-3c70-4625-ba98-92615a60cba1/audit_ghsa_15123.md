# [M] vantage6 has insecure SSH configuration for node and server containers

## Summary
Severity: Medium
Advisory: GHSA-2wgc-48g2-cj5w
CVE: CVE-2024-21653
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-2wgc-48g2-cj5w
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <4.2.0

## Details
### Impact
Nodes and servers get a ssh config by default that permits root login with password authentication. In a proper deployment, the SSH service is not exposed so there is no risk, but not all deployments are ideal. The default should therefore be less permissive.

We will probably opt to completely remove the ssh option as it is only used for debugging. Later, we can add a debug mode where we can activate it if necessary.

### Workarounds
Remove the ssh part from the docker file and build your own docker image

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-2wgc-48g2-cj5w
- https://nvd.nist.gov/vuln/detail/CVE-2024-21653
- https://github.com/vantage6/vantage6/commit/3fcc6e6a8bd1142fd7a558d8fdd2b246e55c8841
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6-server/PYSEC-2024-34.yaml
- https://github.com/vantage6/vantage6
