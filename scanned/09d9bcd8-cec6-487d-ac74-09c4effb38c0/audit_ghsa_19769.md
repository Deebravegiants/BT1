# [C] Qiskit allows arbitrary code execution decoding QPY format versions < 13

## Summary
Severity: Critical
Advisory: GHSA-6m2c-76ff-6vrf
CVE: CVE-2025-2000
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-6m2c-76ff-6vrf
Type: github-advisory

## Affected
- PyPI: `qiskit-terra` — affected >=0.18.0
- PyPI: `qiskit` — affected >=0 <1.4.2
- PyPI: `qiskit` — affected >=2.0.0rc1 <2.0.0rc2

## Details
### Impact

A maliciously crafted QPY file can potentially execute arbitrary-code embedded in the payload without privilege escalation when deserializing QPY formats < 13. A python process calling Qiskit's `qiskit.qpy.load()` function could potentially execute any arbitrary Python code embedded in the correct place in the binary file as part of a specially constructed payload.

### Patches

Fixed in Qiskit 1.4.2 and in Qiskit 2.0.0rc2

## References
- https://github.com/Qiskit/qiskit/security/advisories/GHSA-6m2c-76ff-6vrf
- https://nvd.nist.gov/vuln/detail/CVE-2025-2000
- https://github.com/Qiskit/qiskit
- https://www.ibm.com/support/pages/node/7185949
