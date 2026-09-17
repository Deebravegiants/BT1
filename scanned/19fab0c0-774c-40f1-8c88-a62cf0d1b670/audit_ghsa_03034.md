# [M] Open redirects on some federation and push requests

## Summary
Severity: Medium
Advisory: GHSA-v936-j8gp-9q3p
CVE: CVE-2021-21273
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-02-26
Source: https://github.com/advisories/GHSA-v936-j8gp-9q3p
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.25.0

## Details
### Impact
Requests to user provided domains were not restricted to external IP addresses when calculating the key validity for third-party invite events and sending push notifications. This could cause Synapse to make requests to internal infrastructure. The type of request was not controlled by the user, although limited modification of request bodies was possible.

For the most thorough protection server administrators should remove the deprecated `federation_ip_range_blacklist` from their settings after upgrading to Synapse v1.25.0 which will result in Synapse using the improved default IP address restrictions. See the new `ip_range_blacklist` and `ip_range_whitelist` settings if more specific control is necessary.

### Patches
Issue is resolved by #8821. Further improvements to protect homeservers by default were made in #8870 and #8954.

### Workarounds
Requests to internal IP addresses could be blocked at the system or network level.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-v936-j8gp-9q3p
- https://nvd.nist.gov/vuln/detail/CVE-2021-21273
- https://github.com/matrix-org/synapse/pull/8821
- https://github.com/matrix-org/synapse/commit/30fba6210834a4ecd91badf0c8f3eb278b72e746
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.25.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2021-131.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TNNAJOZNMVMXM6AS7RFFKB4QLUJ4IFEY
