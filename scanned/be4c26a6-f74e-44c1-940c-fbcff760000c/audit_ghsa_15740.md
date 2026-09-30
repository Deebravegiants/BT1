# [H] H2O vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-w36w-948j-xhfw
CVE: CVE-2024-6960
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-21
Source: https://github.com/advisories/GHSA-w36w-948j-xhfw
Type: github-advisory

## Affected
- Maven: `ai.h2o:h2o-core` — affected >=0

## Details
The H2O machine learning platform uses "Iced" classes as the primary means of moving Java Objects around the cluster. The Iced format supports inclusion of serialized Java objects. When a model is deserialized, any class is allowed to be deserialized (no class whitelist). An attacker can construct a crafted Iced model that uses Java gadgets and leads to arbitrary code execution when imported to the H2O platform.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6960
- https://github.com/h2oai/h2o-3
- https://mvnrepository.com/artifact/ai.h2o/h2o-core
- https://research.jfrog.com/vulnerabilities/h2o-model-deserialization-rce-jfsa-2024-001035518
