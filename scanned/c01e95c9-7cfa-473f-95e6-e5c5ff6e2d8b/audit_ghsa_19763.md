# [C] Kedro deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-747f-ww56-4q4h
CVE: CVE-2024-9701
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-747f-ww56-4q4h
Type: github-advisory

## Affected
- PyPI: `kedro` — affected >=0 <0.19.9

## Details
A Remote Code Execution (RCE) vulnerability has been identified in the Kedro ShelveStore class (version 0.19.8). This vulnerability allows an attacker to execute arbitrary Python code via deserialization of malicious payloads, potentially leading to a full system compromise. The ShelveStore class uses Python's shelve module to manage session data, which relies on pickle for serialization. Crafting a malicious payload and storing it in the shelve file can lead to RCE when the payload is deserialized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9701
- https://github.com/kedro-org/kedro/commit/66e5e074b2789469550370f370c8b486f638d975
- https://github.com/kedro-org/kedro
- https://github.com/pypa/advisory-database/tree/main/vulns/kedro/PYSEC-2026-367.yaml
- https://huntr.com/bounties/96c77fef-93b2-4d4d-8cbe-57a718d8eea5
