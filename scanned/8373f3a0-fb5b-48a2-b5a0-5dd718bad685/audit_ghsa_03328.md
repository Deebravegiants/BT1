# [M] Denial of service attack via push rule patterns in matrix-synapse

## Summary
Severity: Medium
Advisory: GHSA-x345-32rc-8h85
CVE: CVE-2021-29471
CWE: CWE-331, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-13
Source: https://github.com/advisories/GHSA-x345-32rc-8h85
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.33.2

## Details
### Impact

"Push rules" can specify [conditions](https://matrix.org/docs/spec/client_server/r0.6.1#conditions) under which they will match, including `event_match`, which matches event content against a pattern including wildcards.

Certain patterns can cause very poor performance in the matching engine, leading to a denial-of-service when processing moderate length events.

### Patches

The issue is patched by https://github.com/matrix-org/synapse/commit/03318a766cac9f8b053db2214d9c332a977d226c.

### Workarounds

A potential workaround might be to prevent users from making custom push rules, by blocking such requests at a reverse-proxy.

### For more information

If you have any questions or comments about this advisory, email us at security@matrix.org.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-x345-32rc-8h85
- https://nvd.nist.gov/vuln/detail/CVE-2021-29471
- https://github.com/matrix-org/synapse/commit/03318a766cac9f8b053db2214d9c332a977d226c
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.33.2
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2021-135.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TNNAJOZNMVMXM6AS7RFFKB4QLUJ4IFEY
