# [H] Rancher's External RoleTemplates can lead to privilege escalation

## Summary
Severity: High
Advisory: GHSA-64jq-m7rq-768h
CVE: CVE-2023-32196
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-64jq-m7rq-768h
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.7.14
- Go: `github.com/rancher/rancher` — affected >=2.8.0 <2.8.5

## Details
### Impact
A vulnerability has been identified whereby privilege escalation checks are not properly enforced for `RoleTemplate`objects when external=true, which in specific scenarios can lead to privilege escalation.

The bug in the webhook rule resolver ignores rules from a `ClusterRole` for external `RoleTemplates` when its context is set to either `project` or is left empty. The fix introduces a new field to the `RoleTemplate` CRD named `ExternalRules`. The new field will be used to resolve rules directly from the `RoleTemplate`. Additionally, rules from the backing `ClusterRole` will be used if `ExternalRules` is not provided. The new field will always take precedence when it is set, and serve as the source of truth for rules used when creating Rancher resources on the local cluster.

Please note that this is a breaking change for external `RoleTemplates`, when context is set to `project` or empty and the backing `ClusterRole` does not exist, as this was not previously required.

**Important:** The fix is automatically applied when upgrading to the release lines `2.8`and above. For users still on the `2.7` release line, after the upgrade to a patched version, users are required to opt-in to the fix by enabling the `external-rules` [feature flag](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/installation-references/feature-flags).

Please consult the associated [MITRE ATT&CK - Technique - Exploitation for Privilege Escalation](https://attack.mitre.org/techniques/T1068/) for further information about this category of attack.

### Patches
Patched versions include releases `2.7.14` and `2.8.5`.

### Workarounds
The following script was developed for Rancher Manager administrators to identify `RoleTemplates` impacted by this vulnerability. The script requires `jq` installed and a `kubeconfig` with access to Rancher local cluster; it can also be executed in Rancher's kubectl shell.

```bash
#!/bin/bash
set -euo pipefail

# get all RoleTemplates with .context == "project" or .context == "" that don't have externalRules.
rts=$(kubectl get roletemplates -o json | jq -r  '.items[] | select((.context == "project" or .context == "") and .external == true and .externalRules == null and .builtin == false) | .metadata.name')
found_invalid_rt=false

for rt in $rts; do
  if ! kubectl get clusterrole "$rt" > /dev/null 2>&1; then
     echo "$rt" # prints RoleTemplate names that don't have a backing ClusterRole
     found_invalid_rt=true
  fi
done

if ! $found_invalid_rt ; then
    echo 'This cluster is not affected by CVE-2023-32197: no RoleTemplate objects found'
fi
```

It will return all objects affected by this vulnerability. The administrator can fix those objects by creating the backing `ClusterRole` that they refer to.


### References
- [CVE-2023-32196](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-32196)

If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security-related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-64jq-m7rq-768h
- https://nvd.nist.gov/vuln/detail/CVE-2023-32196
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-32196
- https://github.com/rancher/rancher
