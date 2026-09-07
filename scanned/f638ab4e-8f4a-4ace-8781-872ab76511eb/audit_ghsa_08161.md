# [H] Boltz contains an insecure deserialization vulnerability in its molecule loading functionality

## Summary
Severity: High
Advisory: GHSA-fjm6-8xp2-4fwc
CVE: CVE-2025-70560
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-fjm6-8xp2-4fwc
Type: github-advisory

## Affected
- PyPI: `boltz` — affected >=0

## Details
Boltz 2.0.0 contains an insecure deserialization vulnerability in its molecule loading functionality. The application uses Python pickle to deserialize molecule data files without validation. An attacker with the ability to place a malicious pickle file in a directory processed by boltz can achieve arbitrary code execution when the file is loaded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70560
- https://github.com/jwohlwend/boltz/issues/600
- https://github.com/jwohlwend/boltz
- https://github.com/jwohlwend/boltz/blob/cb04aeccdd480fd4db707f0bbafde538397fa2ac/src/boltz/data/mol.py#L80
