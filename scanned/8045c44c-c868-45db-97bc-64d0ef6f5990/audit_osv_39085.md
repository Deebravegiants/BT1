# [H] Apache OpenNLP :: Core :: ML :: LibSVM: Unsafe Java Deserialization in SvmDoccatModel

## Summary
Severity: High
Advisory: CVE-2026-43825
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-43825
Type: osv

## Details
Untrusted Java Deserialization in Apache OpenNLP SvmDoccatModel

Versions Affected:
  before 3.0.0-M4 (libsvm document categorization module; introduced in
  OPENNLP-1808 and only present on the 3.x line)

Description:
SvmDoccatModel.deserialize(InputStream) reads an attacker-controlled
stream with java.io.ObjectInputStream and calls readObject() without an
ObjectInputFilter installed. ObjectInputStream materialises every class
referenced in the stream before the resulting object is cast to
SvmDoccatModel, so the cast that follows readObject() executes only
after the foreign object graph has already been deserialised in full.

If a Java deserialization gadget chain is available on the consumer's
classpath, a crafted payload supplied to
deserialize() executes arbitrary code in the JVM that loads it. Apache
OpenNLP itself does not ship a known gadget chain, so the realistic
risk is to downstream applications that embed the libsvm module
alongside vulnerable transitive dependencies. The method is public and
static, so any caller can pass an untrusted stream to it directly.

The practical impact is remote code execution against processes that
load SvmDoccatModel instances from untrusted or semi-trusted origins.

Mitigation:

3.x users should upgrade to 3.0.0-M4.

Users who cannot upgrade immediately should treat all serialized
SvmDoccatModel streams as untrusted input unless their provenance is
verified, and should avoid invoking SvmDoccatModel.deserialize() on
streams supplied by end users or fetched from third-party sources
without integrity checks.

## References
- http://www.openwall.com/lists/oss-security/2026/07/06/9
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43825.json
- https://lists.apache.org/thread/c7kom0pgk9cbpfnbooh5m3g85ndf50hn
- https://nvd.nist.gov/vuln/detail/CVE-2026-43825
