# [M] Velero vulnerable to file path traversal when extracting from backup's tarball

## Summary
Severity: Medium
Advisory: GHSA-j2g6-362q-6qc6
CVE: CVE-2026-32637
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-j2g6-362q-6qc6
Type: github-advisory

## Affected
- Go: `github.com/vmware-tanzu/velero` — affected >=0 <1.18.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
If the attacker compromises the backup's object storage backend and uploads a malicious backup tarball including file names like the following:
* ../../../tmp/escape_1              -> file created at /tmp/escape_1
* ../../../../../../../../tmp/escape_2 -> file created at /tmp/escape_2
* ../../../tmp/cron_poc              -> would be /etc/cron.d/backdoor in real attack
* ../../../tmp/ssh_poc               -> would be ~/.ssh/authorized_keys
* ../../../tmp/kubeconfig_poc        -> would be ~/.kube/config

It's possible that extracting files from the tarball during restore can overwrite sensitive files in the Velero pod filesystem. 

### Patches
_Has the problem been patched? What versions should users upgrade to?_

By far, there is no patch yet.
We are working on the main branch, then cherry-pick to the release-1.18 for v1.18.1 patch.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

There is no workaround, but the good news is that keeping your OSS safe will prevent the vulnerability.

## References
- https://github.com/velero-io/velero/security/advisories/GHSA-j2g6-362q-6qc6
- https://github.com/securego/gosec/issues/324
- https://github.com/velero-io/velero
