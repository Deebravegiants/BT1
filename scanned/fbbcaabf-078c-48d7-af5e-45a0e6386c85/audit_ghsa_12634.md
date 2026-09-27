# [M] Synapse has URL deny list bypass via oEmbed and image URLs when generating previews

## Summary
Severity: Medium
Advisory: GHSA-98px-6486-j7qc
CVE: CVE-2023-32683
CWE: CWE-863, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-98px-6486-j7qc
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.85.0

## Details
### Impact
A discovered oEmbed or image URL can bypass the `url_preview_url_blacklist` setting potentially allowing server side request forgery or bypassing network policies. Impact is limited to IP addresses allowed by the `url_preview_ip_range_blacklist` setting (by default this only allows public IPs) and by the limited information returned to the client:

* For discovered oEmbed URLs, any non-JSON response or a JSON response which includes non-oEmbed information is discarded.
* For discovered image URLs, any non-image response is discarded.

Systems which have URL preview disabled (via the `url_preview_enabled` setting) or have not configured a `url_preview_url_blacklist` are not affected.

Because of the uncommon configuration required, the limited information a malicious user, and the amount of guesses/time the attack would need; the severity is rated as low.

### Patches

The issue is fixed by #15601.

### Workarounds

The default configuration of the `url_preview_ip_range_blacklist` should protect against requests being made to internal infrastructure, URL previews of public URLs is expected.

Alternately URL previews could be disabled using the `url_preview_enabled` setting.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-98px-6486-j7qc
- https://nvd.nist.gov/vuln/detail/CVE-2023-32683
- https://github.com/matrix-org/synapse/pull/15601
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.85.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2023-85.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X6DH5A5YEB5LRIPP32OUW25FCGZFCZU2
