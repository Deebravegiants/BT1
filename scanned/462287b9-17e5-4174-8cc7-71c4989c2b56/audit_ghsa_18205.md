# [H] podman kube play symlink traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-wp3j-xq48-xpjw
CVE: CVE-2025-9566
CWE: CWE-22, CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-wp3j-xq48-xpjw
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v5` — affected >=0 <5.6.1
- Go: `github.com/containers/podman/v4` — affected >=0

## Details
### Impact

The podman kube play command can overwrite host files when the kube file contains a ConfigMap or Secret volume mount and the volume already contains a symlink to a host file.
This allows a malicious container to write to arbitrary files on the host BUT the attacker only controls the target path not the contents that will be written to the file. The contents are defined in the yaml file by the end user.

### Requirements to exploit:
podman kube play must be used with a ConfigMap or Secret volume mount AND must be run more than once on the same volume. All the attacker has to do is create the malicious symlink on the volume the first time it is started. After that all following starts would follow the symlink and write to the host location. 


### Patches
Fixed in podman v5.6.1
https://github.com/containers/podman/commit/43fbde4e665fe6cee6921868f04b7ccd3de5ad89

### Workarounds

Don't use podman kube play with ConfigMap or Secret volume mounts.

### PR with test for CI

Adding on 9/8/2025 by @TomSweeneyRedHat , this is the PR containing the test in CI: https://github.com/containers/podman/pull/27001

## References
- https://github.com/containers/podman/security/advisories/GHSA-wp3j-xq48-xpjw
- https://nvd.nist.gov/vuln/detail/CVE-2025-9566
- https://github.com/containers/podman/commit/43fbde4e665fe6cee6921868f04b7ccd3de5ad89
- https://access.redhat.com/errata/RHSA-2025:18240
- https://access.redhat.com/errata/RHSA-2025:19002
- https://access.redhat.com/errata/RHSA-2025:19041
- https://access.redhat.com/errata/RHSA-2025:19046
- https://access.redhat.com/errata/RHSA-2025:19094
- https://access.redhat.com/errata/RHSA-2025:19894
- https://access.redhat.com/errata/RHSA-2025:20909
- https://access.redhat.com/errata/RHSA-2025:20983
- https://access.redhat.com/errata/RHSA-2026:18289
- https://access.redhat.com/errata/RHSA-2026:18722
- https://access.redhat.com/errata/RHSA-2026:8211
- https://access.redhat.com/security/cve/CVE-2025-9566
- https://bugzilla.redhat.com/show_bug.cgi?id=2393152
- https://github.com/containers/podman
- https://access.redhat.com/errata/RHBA-2025:15692
- https://access.redhat.com/errata/RHBA-2025:15712
- https://access.redhat.com/errata/RHBA-2025:16158
