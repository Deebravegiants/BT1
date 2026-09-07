# [C] Insecure deserialization in BentoML

## Summary
Severity: Critical
Advisory: GHSA-hvj5-mvw9-93j3
CVE: CVE-2024-2912
CWE: CWE-1188
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-hvj5-mvw9-93j3
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.2.5

## Details
An insecure deserialization vulnerability exists in the BentoML framework, allowing remote code execution (RCE) by sending a specially crafted POST request. By exploiting this vulnerability, attackers can execute arbitrary commands on the server hosting the BentoML application. The vulnerability is triggered when a serialized object, crafted to execute OS commands upon deserialization, is sent to any valid BentoML endpoint. This issue poses a significant security risk, enabling attackers to compromise the server and potentially gain unauthorized access or control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2912
- https://github.com/bentoml/bentoml/commit/fd70379733c57c6368cc022ac1f841b7b426db7b
- https://github.com/bentoml/BentoML
- https://huntr.com/bounties/349a1cce-6bb5-4345-82a5-bf7041b65a68
