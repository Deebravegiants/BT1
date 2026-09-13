# [M] DockerSpawner allows any image by default

## Summary
Severity: Medium
Advisory: GHSA-hfgr-h3vc-p6c2
CVE: CVE-2023-48311
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-hfgr-h3vc-p6c2
Type: github-advisory

## Affected
- PyPI: `dockerspawner` — affected >=0.11.0 <13.0.0

## Details
### Impact

Users of JupyterHub deployments running DockerSpawner starting with 0.11.0 without specifying `DockerSpawner.allowed_images` configuration allow users to launch _any_ pullable image, instead of restricting to only the single configured image, as intended.

### Patches

Upgrade to DockerSpawner 13.

### Workarounds

Explicitly setting `DockerSpawner.allowed_images` to a non-empty list containing only the default image will result in the intended default behavior:

```python
c.DockerSpawner.image = "your-image"
c.DockerSpawner.allowed_images = ["your-image"]
```

## References
- https://github.com/jupyterhub/dockerspawner/security/advisories/GHSA-hfgr-h3vc-p6c2
- https://nvd.nist.gov/vuln/detail/CVE-2023-48311
- https://github.com/jupyterhub/dockerspawner/commit/3ba4b665b6ca6027ea7a032d7ca3eab977574626
- https://github.com/jupyterhub/dockerspawner
