# [M] jackson-databind resolves attacker-controlled URI schemes when deserializing java.nio.file.Path

## Summary
Severity: Medium
Advisory: CVE-2026-19032
Aliases: GHSA-wjgm-6hv5-3cvf
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-19032
Type: osv

## Details
jackson-databind's deserializer for java.nio.file.Path resolves an attacker-supplied URI without restricting the URI scheme. In JDKFromStringDeserializer.NioPathHelper.deserialize, a string bound from untrusted JSON is passed to new URI(value) and then to Path.of(uri). When that throws FileSystemNotFoundException, the code enumerates ServiceLoader<FileSystemProvider> and calls provider.getPath(uri) on the first provider whose scheme matches the attacker-chosen scheme. Untrusted JSON can therefore select and drive an arbitrary registered FileSystemProvider during readValue under a default JsonMapper, and forces provider class loading at the same time. With only the JDK built-in providers (file, jar/zipfs) present, the resolved path is inert and no mount or network I/O occurs; further impact requires a side-effecting third-party FileSystemProvider on the classpath. This affects com.fasterxml.jackson.core:jackson-databind from 2.8.0 before 2.18.10, from 2.19.0 before 2.21.6, and from 2.22.0 before 2.22.2, and tools.jackson.core:jackson-databind from 3.0.0 before 3.1.6 and from 3.2.0 before 3.2.2. Users should upgrade to 2.18.10, 2.21.6, 2.22.2, 3.1.6, or 3.2.2. Binding java.nio.file.Path from untrusted JSON should be avoided regardless of version.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19032.json
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-wjgm-6hv5-3cvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-19032
- https://github.com/FasterXML/jackson-databind/commit/cc6756b61ed90b6b9227f670e0408d5d9bd48551
- https://github.com/FasterXML/jackson-databind/commit/ce26eda3481cd796f76ba4c53ffe1da23b53f166
- https://github.com/FasterXML/jackson-databind/commit/d94bb632becfe0ba96926b9909ab06d1f87aad6d
- https://github.com/FasterXML/jackson-databind/pull/6129
- https://github.com/FasterXML/jackson-databind
