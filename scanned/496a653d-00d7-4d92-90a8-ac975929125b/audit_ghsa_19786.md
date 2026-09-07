# [M] H2O Vulnerable to Execution of Arbitrary Files

## Summary
Severity: Medium
Advisory: GHSA-m37h-8r48-2cxj
CVE: CVE-2024-6863
CWE: CWE-749
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-m37h-8r48-2cxj
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=3.32.1.2
- Maven: `ai.h2o:h2o-core` — affected >=3.32.1.2

## Details
In h2oai/h2o-3 version 3.46.0, an endpoint exposing a custom EncryptionTool allows an attacker to encrypt any files on the target server with a key of their choosing. The chosen key can also be overwritten, resulting in ransomware-like behavior. This vulnerability makes it possible for an attacker to encrypt arbitrary files with keys of their choice, making it exceedingly difficult for the target to recover the keys needed for decryption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6863
- https://github.com/h2oai/h2o-3
- https://github.com/h2oai/h2o-3/blob/a20b5b19b769866ee24b217ee78b820e64c1cd6a/h2o-core/src/main/java/water/tools/EncryptionTool.java#L49
- https://huntr.com/bounties/10f55937-0cba-4530-897f-2abf30ed5270
