# [H] Synapse denial of service through media disk space consumption

## Summary
Severity: High
Advisory: GHSA-4mhg-xv73-xq2x
CVE: CVE-2024-37302
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-4mhg-xv73-xq2x
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.106

## Details
### Impact

Synapse versions before 1.106 are vulnerable to a disk fill attack, where an unauthenticated adversary can induce Synapse to download and cache large amounts of remote media. The default rate limit strategy is insufficient to mitigate this. This can lead to a denial of service, ranging from further media uploads/downloads failing to completely unavailability of the Synapse process, depending on how Synapse was deployed.

### Patches

Synapse 1.106 introduces a new "leaky bucket" rate limit on remote media downloads to reduce the amount of data a user can request at a time. This does not fully address the issue, but does limit an unauthenticated user's ability to request large amounts of data to be cached.

### Workarounds

Synapse deployments can currently decrease the maximum file size allowed, as well as increase request rate limits. However, this does not as effectively address the issue as a dedicated rate limit on remote media downloads.

Server operators may also wish to consider putting media on a dedicated disk or volume, reducing the impact of a disk fill condition.

### References

* https://en.wikipedia.org/wiki/Leaky_bucket#As_a_meter

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-4mhg-xv73-xq2x
- https://nvd.nist.gov/vuln/detail/CVE-2024-37302
- https://github.com/element-hq/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2024-286.yaml
