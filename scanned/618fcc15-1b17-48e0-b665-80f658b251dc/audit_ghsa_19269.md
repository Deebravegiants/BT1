# [M] HumanSignal label-studio-ml-backend Deserialization of Untrusted Data vulnerability

## Summary
Severity: Medium
Advisory: GHSA-55g9-6c2x-gf8q
CVE: CVE-2025-5173
CWE: CWE-20, CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-05-26
Source: https://github.com/advisories/GHSA-55g9-6c2x-gf8q
Type: github-advisory

## Affected
- PyPI: `label-studio-ml` — affected >=0

## Details
A vulnerability has been found in HumanSignal label-studio-ml-backend up to 9fb7f4aa186612806af2becfb621f6ed8d9fdbaf and classified as problematic. Affected by this vulnerability is the function load of the file label-studio-ml-backend/label_studio_ml/examples/yolo/utils/neural_nets.py of the component PT File Handler. The manipulation of the argument path leads to deserialization. An attack has to be approached locally. This product takes the approach of rolling releases to provide continious delivery. Therefore, version details for affected and updated releases are not available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5173
- https://github.com/HumanSignal/label-studio-ml-backend/issues/765
- https://github.com/HumanSignal/label-studio-ml-backend
- https://vuldb.com/?ctiid.310261
- https://vuldb.com/?id.310261
- https://vuldb.com/?submit.578126
