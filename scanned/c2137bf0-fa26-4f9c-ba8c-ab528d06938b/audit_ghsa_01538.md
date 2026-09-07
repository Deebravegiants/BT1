# [H] Possible pod name collisions in jupyterhub-kubespawner

## Summary
Severity: High
Advisory: GHSA-v7m9-9497-p9gr
CVE: CVE-2020-15110
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-07-22
Source: https://github.com/advisories/GHSA-v7m9-9497-p9gr
Type: github-advisory

## Affected
- PyPI: `jupyterhub-kubespawner` — affected >=0 <0.12.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

JupyterHub deployments using:

- KubeSpawner <= 0.11.1 (e.g. zero-to-jupyterhub 0.9.0) and
- enabled named_servers (not default), and
- an Authenticator that allows:
  - usernames with hyphens or other characters that require escape (e.g. `user-hyphen` or `user@email`), and
  - usernames which may match other usernames up to but not including the escaped character (e.g. `user` in the above cases)

In this circumstance, certain usernames will be able to craft particular server names which will grant them access to the default server of other users who have matching usernames.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Patch will be released in kubespawner 0.12 and zero-to-jupyterhub 0.9.1

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

#### KubeSpawner

Specify configuration:

for KubeSpawner
```python
from traitlets import default
from kubespawner import KubeSpawner

class PatchedKubeSpawner(KubeSpawner):
    @default("pod_name_template")
    def _default_pod_name_template(self):
        if self.name:
            return "jupyter-{username}-{servername}"
        else:
            return "jupyter-{username}"

    @default("pvc_name_template")
    def _default_pvc_name_template(self):
        if self.name:
            return "claim-{username}-{servername}"
        else:
            return "claim-{username}"

c.JupyterHub.spawner_class = PatchedKubeSpawner
```

**Note for KubeSpawner:** this configuration will behave differently before and after the upgrade, so will need to be removed when upgrading. Only apply this configuration while still using KubeSpawner ≤ 0.11.1 and remove it after upgrade to ensure consistent pod and pvc naming.

Changing the name template means pvcs for named servers will have different names. This will result in orphaned PVCs for named servers across Hub upgrade! This may appear as data loss for users, depending on configuration, but the orphaned PVCs will still be around and data can be migrated manually (or new PVCs created manually to reference existing PVs) before deleting the old PVCs and/or PVs.

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [kubespawner](https://github.com/jupyterhub/kubespawner)
* Email us at [security@ipython.org](mailto:security@ipython.org)

Credit: Jining Huang

## References
- https://github.com/jupyterhub/kubespawner/security/advisories/GHSA-v7m9-9497-p9gr
- https://nvd.nist.gov/vuln/detail/CVE-2020-15110
- https://github.com/jupyterhub/kubespawner/commit/3dfe870a7f5e98e2e398b01996ca6b8eff4bb1d0
- https://github.com/jupyterhub/kubespawner
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterhub-kubespawner/PYSEC-2020-51.yaml
