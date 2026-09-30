# [C] CVE-2025-12977

## Summary
Severity: Critical
Advisory: BIT-fluent-bit-2025-12977
Aliases: CVE-2025-12977
Ecosystem: Bitnami
Published: 2025-12-01
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2025-12977
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=4.1.0 <4.1.1

## Details
Fluent Bit in_http, in_splunk, and in_elasticsearch input plugins fail to sanitize tag_key inputs. An attacker with network access or the ability to write records into Splunk or Elasticsearch can supply tag_key values containing special characters such as newlines or ../ that are treated as valid tags. Because tags influence routing and some outputs derive filenames or contents from tags, this can allow newline injection, path traversal, forged record injection, or log misrouting, impacting data integrity and log routing.

## References
- https://fluentbit.io/blog/2025/10/28/security-vulnerabilities-addressed-in-fluent-bit-v4.1-and-backported-to-v4.0/
- https://nvd.nist.gov/vuln/detail/CVE-2025-12977
- https://www.oligo.security/blog/critical-vulnerabilities-in-fluent-bit-expose-cloud-environments-to-remote-takeover
