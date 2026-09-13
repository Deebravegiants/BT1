# [C] Improper Limitation of a Pathname to a Restricted Directory in Logstash Leading to Arbitrary File Write

## Summary
Severity: Critical
Advisory: BIT-logstash-2026-33466
Aliases: CVE-2026-33466
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-logstash-2026-33466
Type: osv

## Affected
- Bitnami: `logstash` — affected >=9.3.0 <9.3.3

## Details
Improper Limitation of a Pathname to a Restricted Directory (CWE-22) in Logstash can lead to arbitrary file write and potentially remote code execution via Relative Path Traversal (CAPEC-139). The archive extraction utilities used by Logstash do not properly validate file paths within compressed archives. An attacker who can serve a specially crafted archive to Logstash through a compromised or attacker-controlled update endpoint can write arbitrary files to the host filesystem with the privileges of the Logstash process. In certain configurations where automatic pipeline reloading is enabled, this can be escalated to remote code execution.

## References
- https://discuss.elastic.co/t/logstash-8-19-14-9-2-8-9-3-3-security-update-esa-2026-29/385816
- https://nvd.nist.gov/vuln/detail/CVE-2026-33466
