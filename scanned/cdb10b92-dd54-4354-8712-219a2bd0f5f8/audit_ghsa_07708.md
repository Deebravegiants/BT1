# [H] Google Cloud Vertex AI SDK affected by Stored Cross-Site Scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-qv8j-hgpc-vrq8
CVE: CVE-2026-2472
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L/U:Amber (CVSS_V4)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-qv8j-hgpc-vrq8
Type: github-advisory

## Affected
- PyPI: `google-cloud-aiplatform` — affected >=1.98.0 <1.131.0

## Details
Stored Cross-Site Scripting (XSS) in the _genai/_evals_visualization component of Google Cloud Vertex AI SDK (google-cloud-aiplatform) versions from 1.98.0 up to (but not including) 1.131.0 allows an unauthenticated remote attacker to execute arbitrary JavaScript in a victim's Jupyter or Colab environment via injecting script escape sequences into model evaluation results or dataset JSON data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2472
- https://github.com/googleapis/python-aiplatform/commit/8a00d43dbd24e95dbab6ea32c63ce0a5a1849480
- https://docs.cloud.google.com/support/bulletins#gcp-2026-011
- https://github.com/JoshuaProvoste/CVE-2026-2472-Vertex-AI-SDK-Google-Cloud
- https://github.com/googleapis/python-aiplatform
- https://github.com/googleapis/python-aiplatform/releases/tag/v1.131.0
