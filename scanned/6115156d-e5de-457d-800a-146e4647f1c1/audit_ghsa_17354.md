# [H] KEDA has Arbitrary File Read via Insufficient Path Validation in HashiCorp Vault Service Account Credential

## Summary
Severity: High
Advisory: GHSA-c4p6-qg4m-9jmr
CVE: CVE-2025-68476
CWE: CWE-22, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-12-22
Source: https://github.com/advisories/GHSA-c4p6-qg4m-9jmr
Type: github-advisory

## Affected
- Go: `github.com/kedacore/keda/v2` — affected >=2.18.0 <2.18.3
- Go: `github.com/kedacore/keda/v2` — affected >=0 <2.17.3

## Details
### Impact
An Arbitrary File Read vulnerability has been identified in KEDA, potentially affecting any KEDA resource that uses TriggerAuthentication to configure HashiCorp Vault authentication.

The vulnerability stems from an incorrect or insufficient path validation when loading the Service Account Token specified in spec.hashiCorpVault.credential.serviceAccount.

An attacker with permissions to create or modify a TriggerAuthentication resource can exfiltrate the content of any file from the node's filesystem (where the KEDA pod resides) by directing the file's content to a server under their control, as part of the Vault authentication request.

The potential impact includes the exfiltration of sensitive system information, such as secrets, keys, or the content of files like /etc/passwd.

### Patches
The problem has been patched in v2.17.3 and 2.18.3 as well as in main branch.

### Workarounds
The only effective workaround is the strict restriction of permissions for creating and modifying TriggerAuthentication resources within the Kubernetes cluster.

Only trusted and authorized users should have create or update permissions on the TriggerAuthentication resource.

This limits an attacker's ability to configure a malicious TriggerAuthentication with an arbitrary path.

### Is my project affected?
If it execute s
```bash
kubectl get deploy keda-operator -n keda -o jsonpath="{.spec.template.spec.containers[0].image}"
```
and the version is not 2.17.3, 2.18.3 or >= 2.19.0, that version is affected.

## References
- https://github.com/kedacore/keda/security/advisories/GHSA-c4p6-qg4m-9jmr
- https://nvd.nist.gov/vuln/detail/CVE-2025-68476
- https://github.com/kedacore/keda/commit/15c5677f65f809b9b6b59a52f4cf793db0a510fd
- https://github.com/kedacore/keda
