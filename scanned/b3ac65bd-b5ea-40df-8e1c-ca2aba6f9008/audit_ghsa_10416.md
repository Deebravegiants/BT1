# [M] Apache Storm Prometheus Reporter vulnerable to Improper Certificate Validation via Global SSL Context Downgrade

## Summary
Severity: Medium
Advisory: GHSA-82fm-wpc2-5pmp
CVE: CVE-2026-40557
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-82fm-wpc2-5pmp
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm-metrics-prometheus` — affected >=2.6.3 <2.8.7

## Details
Improper Certificate Validation via Global SSL Context Downgrade in Apache Storm Prometheus Reporter


Versions Affected: from 2.6.3 to 2.8.6


Description: 

In production deployments where an administrator enables storm.daemon.metrics.reporter.plugin.prometheus.skip_tls_validation (by default it is disabled) intending to affect only the Prometheus reporter, the undocumented global side effect creates an attack surface across every TLS-protected communication channel in the Storm daemon.


The PrometheusPreparableReporter class implements an INSECURE_TRUST_MANAGER that accepts all SSL certificates without validation, with empty checkClientTrusted and checkServerTrusted methods. Most critically, when the storm.daemon.metrics.reporter.plugin.prometheus.skip_tls_validation configuration option is enabled (default = disabled) for HTTPS Prometheus PushGateway connections, the INSECURE_CONNECTION_FACTORY calls SSLContext.setDefault(sslContext), which globally replaces the JVM's default SSL context rather than applying the insecure context only to the Prometheus connection. This payload flows through storm.yaml configuration → PrometheusPreparableReporter.prepare() → INSECURE_CONNECTION_FACTORY → SSLContext.setDefault(), resulting in a JVM-wide TLS security downgrade. All subsequent HTTPS connections in the process - including ZooKeeper, Thrift, Netty, and UI connections - silently trust all certificates, including self-signed, expired, and attacker-generated ones, enabling man-in-the-middle interception of cluster state, topology submissions, tuple data, and administrative credentials.




Mitigation: 2.x users should upgrade to 2.8.7 if the Prometheus Metrics Reporter is used. Prometheus Metrics Reporter Users who cannot upgrade immediately should remove the storm.daemon.metrics.reporter.plugin.prometheus.skip_tls_validation: true setting from their storm.yaml configuration and instead configure a proper truststore containing the PushGateway's certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40557
- https://github.com/apache/storm
- https://lists.apache.org/thread/f5bv68z1y5xstz22psjk05p3wn86knjq
- http://www.openwall.com/lists/oss-security/2026/04/25/2
