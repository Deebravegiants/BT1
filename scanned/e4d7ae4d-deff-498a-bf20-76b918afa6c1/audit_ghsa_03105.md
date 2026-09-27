# [M] Improper Handling of Highly Compressed Data (Data Amplification) and Memory Allocation with Excessive Size Value in eventlet

## Summary
Severity: Medium
Advisory: GHSA-9p9m-jm8w-94p2
CVE: CVE-2021-21419
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-9p9m-jm8w-94p2
Type: github-advisory

## Affected
- PyPI: `eventlet` — affected >=0.10 <0.31.0

## Details
### Impact
A websocket peer may exhaust memory on Eventlet side by sending very large websocket frames. Malicious peer may exhaust memory on Eventlet side by sending highly compressed data frame.

### Patches
Version 0.31.0 restricts websocket frame to reasonable limits.

### Workarounds
Restricting memory usage via OS limits would help against overall machine exhaustion. No workaround to protect Eventlet process.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [eventlet](https://github.com/eventlet/eventlet/issues)
* Contact current maintainers. At 2021-03: temotor@gmail.com or https://t.me/temotor

## References
- https://github.com/eventlet/eventlet/security/advisories/GHSA-9p9m-jm8w-94p2
- https://nvd.nist.gov/vuln/detail/CVE-2021-21419
- https://github.com/eventlet/eventlet/commit/1412f5e4125b4313f815778a1acb4d3336efcd07
- https://github.com/eventlet/eventlet
- https://github.com/pypa/advisory-database/tree/main/vulns/eventlet/PYSEC-2021-12.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2WJFSBPLCNSZNHYQC4QDRDFRTEZRMD2L
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R5JZP4LZOSP7CUAM3GIRW6PIAWKH5VGB
