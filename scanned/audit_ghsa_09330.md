# [H] MLflow Has a Server-Side Request Forgery (SSRF) Vulnerability

## Summary
Severity: High
Advisory: GHSA-65h7-c7c4-mghx
CVE: CVE-2026-2393
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-65h7-c7c4-mghx
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.9.0

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in MLflow versions prior to 3.9.0. The `_create_webhook()` function in `mlflow/server/handlers.py` accepts a user-controlled `url` parameter without validation, and the `_send_webhook_request()` function in `mlflow/webhooks/delivery.py` sends HTTP POST requests to this attacker-controlled URL. This allows an authenticated attacker to force the MLflow backend to send HTTP requests to internal services, cloud metadata endpoints, or arbitrary external servers. The lack of input sanitization, URL scheme filtering, or allowlist validation on the webhook URL enables exploitation, potentially leading to cloud credential theft, internal network access, and data exfiltration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2393
- https://github.com/mlflow/mlflow/commit/64aa0ab7207f9c649b59ba1a5f40d82196817389
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/04ef100d-06b5-4a70-95b1-b7be23aa8150
