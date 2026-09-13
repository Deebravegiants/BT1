# [H] External Secrets Operator vulnerable to privilege escalation

## Summary
Severity: High
Advisory: GHSA-qwgc-rr35-h4x9
CVE: CVE-2024-45041
CWE: CWE-269, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2024-09-09
Source: https://github.com/advisories/GHSA-qwgc-rr35-h4x9
Type: github-advisory

## Affected
- Go: `github.com/external-secrets/external-secrets` — affected >=0 <0.10.2

## Details
### Details
The external-secrets has a deployment called default-external-secrets-cert-controller, which is bound with a same-name ClusterRole. This ClusterRole has "get/list" verbs of secrets resources(https://github.com/external-secrets/external-secrets/blob/main/deploy/charts/external-secrets/templates/cert-controller-rbac.yaml#L49). It also has path/update verb of validatingwebhookconfigurations resources(https://github.com/external-secrets/external-secrets/blob/main/deploy/charts/external-secrets/templates/cert-controller-rbac.yaml#L27). As a result, if a malicious user can access the worker node which has this deployment. he/she can:
1. For the "get/list secrets" permission, he/she can abuse the SA token of this deployment to retrieve or get ALL secrets in the whole cluster, including the cluster-admin secret if created. After that, he/she can abuse the cluster-admin secret to do whatever he/she likes to the whole cluster, resulting in a cluster-level privilege escalation.

2. For the patch/update verb of validatingwebhookconfigurations, the malicious user can abuse these permissions to get sensitive data or lanuch DoS attacks:

For the privilege escalation attack, by updating/patching a Webhook to make it listen to Secret update operations, the attacker can capture and log all data from requests attempting to update Secrets. More specifically, when a Secret is updated, this Webhook sends the request data to the logging-service, which can then log the content of the Secret. This way, an attacker could indirectly gain access to the full contents of the Secret.

For the DoS attack, by updating/patching a Webhook, and making it deny all Pod create and update requests, the attacker can prevent any new Pods from being created or existing Pods from being updated, resulting in a Denial of Service (DoS) attack.

### PoC
Please see the "Details" section

### Impact
Privilege escalation

## References
- https://github.com/external-secrets/external-secrets/security/advisories/GHSA-qwgc-rr35-h4x9
- https://nvd.nist.gov/vuln/detail/CVE-2024-45041
- https://github.com/external-secrets/external-secrets/commit/0368b9806f660fa6bc52cbbf3c6ccdb27c58bb35
- https://github.com/external-secrets/external-secrets/commit/428a452fd2ad45935312f2c2c0d40bc37ce6e67c
- https://github.com/external-secrets/external-secrets
- https://github.com/external-secrets/external-secrets/blob/main/deploy/charts/external-secrets/templates/cert-controller-rbac.yaml#L27
- https://github.com/external-secrets/external-secrets/blob/main/deploy/charts/external-secrets/templates/cert-controller-rbac.yaml#L49
- https://pkg.go.dev/vuln/GO-2024-3126
