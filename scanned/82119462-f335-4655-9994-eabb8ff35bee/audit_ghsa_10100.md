# [H] InstructLab Includes Functionality from Untrusted Control Sphere

## Summary
Severity: High
Advisory: GHSA-rxpq-xgqx-fr7p
CVE: CVE-2026-6859
CWE: CWE-829
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-rxpq-xgqx-fr7p
Type: github-advisory

## Affected
- PyPI: `instructlab` — affected >=0

## Details
A flaw was found in InstructLab. The `linux_train.py` script hardcodes `trust_remote_code=True` when loading models from HuggingFace. This allows a remote attacker to achieve arbitrary Python code execution by convincing a user to run `ilab train/download/generate` with a specially crafted malicious model from the HuggingFace Hub. This vulnerability can lead to complete system compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6859
- https://access.redhat.com/security/cve/CVE-2026-6859
- https://bugzilla.redhat.com/show_bug.cgi?id=2459998
- https://github.com/instructlab/instructlab
