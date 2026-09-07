# [M] kube-audit-rest's example logging configuration could disclose secret values in the audit log

## Summary
Severity: Medium
Advisory: GHSA-hcr5-wv4p-h2g2
CVE: CVE-2025-24884
CWE: CWE-200, CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-hcr5-wv4p-h2g2
Type: github-advisory

## Affected
- Go: `github.com/RichardoC/kube-audit-rest` — affected >=0 <0.0.0-20250205113217-9df8886b4819

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
If the "full-elastic-stack" example vector configuration was used for a real cluster, the previous values of kubernetes secrets would have been disclosed in the audit messages.

### Patches
_Has the problem been patched? What versions should users upgrade to?_
The example has been updated to fix this in commit 9df8886b4819409f566233adc7c3b7a43a4096ba


### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
Replace 
```yaml

          if .request.requestKind.kind == "Secret" {
            del(.request.object.data)
            .request.object.data.redacted = "REDACTED"
            del(.request.oldObject.data)
            .request.oldObject.data.redacted = "REDACTED"
          }
```
In the vector "audit-files-json-parser-and-redaction" step
with
```yaml

          if .request.requestKind.kind == "Secret" {
            # Redact the secret data
            del(.request.object.data)
            .request.object.data.redacted = "REDACTED"
            del(.request.oldObject.data)
            .request.oldObject.data.redacted = "REDACTED"
            # Remove the previously set secret data - Not bothering to parse it as this annotation shouldn't ever be needed
            del(.request.object.metadata.annotations.["kubectl.kubernetes.io/last-applied-configuration"])
            del(.request.oldObject.metadata.annotations.["kubectl.kubernetes.io/last-applied-configuration"])
          }
```


### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/RichardoC/kube-audit-rest/security/advisories/GHSA-hcr5-wv4p-h2g2
- https://nvd.nist.gov/vuln/detail/CVE-2025-24884
- https://github.com/RichardoC/kube-audit-rest/commit/db1aa5b867256b0a7bf206544c6981ab068b73dc
- https://github.com/RichardoC/kube-audit-rest
- https://pkg.go.dev/vuln/GO-2025-3431
