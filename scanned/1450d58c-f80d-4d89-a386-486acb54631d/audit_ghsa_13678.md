# [H] vantage6-server node accepts non-whitelisted algorithms from malicious server

## Summary
Severity: High
Advisory: GHSA-vc3v-ppc7-v486
CVE: CVE-2023-47631
CWE: CWE-345, CWE-358
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-vc3v-ppc7-v486
Type: github-advisory

## Affected
- PyPI: `vantage6-server` — affected >=0 <4.1.2
- PyPI: `vantage6-node` — affected >=0 <4.1.2

## Details
### Impact
A node does not check if an image is allowed to run if a `parent_id` is set. A malicious party that breaches the server may modify it to set a fake `parent_id` and send a task of a non-whitelisted algorithm. The node will then execute it because the `parent_id` that is set prevents checks from being run. Relevant node code [here](https://github.com/vantage6/vantage6/blob/version/4.1.1/vantage6-node/vantage6/node/docker/docker_manager.py#L265-L268)

This impacts all servers that are breached by an expert user

### Patches
Fixed in v4.1.2

### Workarounds
None

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-vc3v-ppc7-v486
- https://nvd.nist.gov/vuln/detail/CVE-2023-47631
- https://github.com/vantage6/vantage6/commit/bf83521eb12fa80aa5fc92ef1692010a9a7f8243
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6-node/PYSEC-2023-303.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6-server/PYSEC-2023-304.yaml
- https://github.com/vantage6/vantage6
- https://github.com/vantage6/vantage6/blob/version/4.1.1/vantage6-node/vantage6/node/docker/docker_manager.py#L265-L268
