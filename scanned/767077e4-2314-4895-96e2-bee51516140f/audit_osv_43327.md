# [C] Prowler: RCE on Prowler App workers via kubeconfig auth-provider cmd-path

## Summary
Severity: Critical
Advisory: CVE-2026-73263
Aliases: GHSA-ccqh-6cjc-wp4j
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73263
Type: osv

## Details
Prowler is a cloud security platform. Prior to 5.36.0, the Kubernetes provider connection test accepted kubeconfig_content containing a legacy gcp auth-provider with config.cmd-path and config.cmd-args because kubeconfig_contains_exec_auth in api/src/backend/api/v1/serializers.py checked only exec blocks, and POST /api/v1/providers/{id}/connection loaded it through config.load_kube_config_from_dict in prowler/providers/kubernetes/kubernetes_provider.py, causing kubernetes-python CommandTokenSource.token to run the attacker-supplied command through subprocess.Popen on the shared worker. This issue is fixed in version 5.36.0.

## References
- https://github.com/prowler-cloud/prowler/releases/tag/5.36.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73263.json
- https://github.com/prowler-cloud/prowler/security/advisories/GHSA-ccqh-6cjc-wp4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-73263
- https://github.com/prowler-cloud/prowler/commit/0b782fcb8c24ece7bd38deede2b8f13d8583e39c
- https://github.com/prowler-cloud/prowler/pull/12091
