# [H]  RCE via ZipSlip and symbolic links in argoproj/argo-workflows

## Summary
Severity: High
Advisory: GHSA-xrqc-7xgx-c9vh
CVE: CVE-2025-66626
CWE: CWE-23, CWE-59, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-xrqc-7xgx-c9vh
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.7.0 <3.7.5
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=0 <3.6.14
- Go: `github.com/argoproj/argo-workflows` — affected >=0

## Details
### Summary
The patch deployed against CVE-2025-62156 is ineffective against malicious archives containing symbolic links.

### Details
The untar code that handles symbolic links in archives is unsafe. Concretely, the computation of the link's target and the subsequent check are flawed: 
https://github.com/argoproj/argo-workflows/blob/5291e0b01f94ba864f96f795bb500f2cfc5ad799/workflow/executor/executor.go#L1034-L1037

### PoC
1. Create a malicious archive containing two files: a symbolik link with path "./work/foo" and target "/etc", and a normal text file with path "./work/foo/hostname".
2. Deploy a workflow like the one in https://github.com/argoproj/argo-workflows/security/advisories/GHSA-p84v-gxvw-73pf with the malicious archive mounted at /work/tmp.
3. Submit the workflow and wait for its execution. 
4. Connect to the corresponding pod and observe that the file "/etc/hostname" was altered by the untar operation performed on the malicious archive. The attacker can hence alter arbitrary files in this way. 

### Impact
The attacker can overwrite the file /var/run/argo/argoexec with a script of their choice, which will be executed at the pod's start.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-xrqc-7xgx-c9vh
- https://nvd.nist.gov/vuln/detail/CVE-2025-66626
- https://github.com/argoproj/argo-workflows/commit/6b92af23f35aed4d4de8b04adcaf19d68f006de1
- https://github.com/advisories/GHSA-p84v-gxvw-73pf
- https://github.com/argoproj/argo-workflows
- https://github.com/argoproj/argo-workflows/blob/5291e0b01f94ba864f96f795bb500f2cfc5ad799/workflow/executor/executor.go#L1034-L1037
