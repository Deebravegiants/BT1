# [M] iq80 Snappy out-of-bounds read when uncompressing data, leading to JVM crash

## Summary
Severity: Medium
Advisory: GHSA-8wh2-6qhj-h7j9
CVE: CVE-2024-36124
CWE: CWE-125
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-8wh2-6qhj-h7j9
Type: github-advisory

## Affected
- Maven: `org.iq80.snappy:snappy` — affected >=0 <0.5

## Details
### Summary
iq80 Snappy performs out-of-bounds read access when uncompressing certain data, which can lead to a JVM crash.

### Details
When uncompressing certain data, Snappy tries to read outside the bounds of the given byte arrays. Because Snappy uses the JDK class `sun.misc.Unsafe` to speed up memory access, no additional bounds checks are performed and this has similar security consequences as out-of-bounds access in C or C++, namely it can lead to non-deterministic behavior or crash the JVM.

iq80 Snappy is not actively maintained anymore. As quick fix users can upgrade to version 0.5, but in the long term users should prefer migrating to the Snappy implementation in https://github.com/airlift/aircompressor (version 0.27 or newer).

### Impact
When uncompressing data from untrusted users, this can be exploited for a denial-of-service attack by crashing the JVM.

## References
- https://github.com/dain/snappy/security/advisories/GHSA-8wh2-6qhj-h7j9
- https://nvd.nist.gov/vuln/detail/CVE-2024-36124
- https://github.com/dain/snappy
