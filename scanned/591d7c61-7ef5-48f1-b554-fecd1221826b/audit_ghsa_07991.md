# [H] Google Cloud Vertex AI has a a vulnerability involving predictable bucket naming

## Summary
Severity: High
Advisory: GHSA-wh2j-26j7-9728
CVE: CVE-2026-2473
CWE: CWE-340
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/U:Clear (CVSS_V4)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-wh2j-26j7-9728
Type: github-advisory

## Affected
- PyPI: `google-cloud-aiplatform` — affected >=1.21.0 <1.133.0

## Details
Predictable bucket naming in Vertex AI Experiments in Google Cloud Vertex AI from version 1.21.0 up to (but not including) 1.133.0 on Google Cloud Platform allows an unauthenticated remote attacker to achieve cross-tenant remote code execution, model theft, and poisoning via pre-creating predictably named Cloud Storage buckets (Bucket Squatting).

This vulnerability was patched and no customer action is needed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2473
- https://docs.cloud.google.com/support/bulletins#gcp-2026-012
- https://github.com/googleapis/python-aiplatform
- https://github.com/googleapis/python-aiplatform/releases/tag/v1.133.0
