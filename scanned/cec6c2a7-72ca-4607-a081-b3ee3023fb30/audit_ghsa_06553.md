# [M] JupyterLab: PyPI extension blocklist package-name canonicalization bypass

## Summary
Severity: Medium
Advisory: GHSA-89vp-jrxv-24w8
CVE: CVE-2026-73416
CWE: CWE-178, CWE-180
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-89vp-jrxv-24w8
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=4.6.0 <4.6.2
- PyPI: `jupyterlab` — affected >=4.5.0 <4.5.10

## Details
JupyterLab's PyPI extension manager enforces `blocked_extensions_uris` by comparing the requested install name to blocklist entries with a custom string normalization that is weaker than PyPI package-name canonicalization. An authenticated user can request a PyPI-equivalent spelling such as `JupyterLab.Git` for a blocklisted package such as `jupyterlab-git`; JupyterLab accepts the install request even though pip resolves the variant to the same package.

This has security implications only for deployments that combine all of the following:
- an allowlist/blocklist configured with the intent of restricting which packages users can install;
- the (default) PyPI Extension Manager enabled; and
- kernels and terminals disabled or delegated to remote hosts (otherwise a user with kernel access can install packages directly regardless of this check) 

### Impact

The vulnerability lets an authenticated user install a package the operator specifically intended to block, defeating the allowlist/blocklist control. Because extensions in principle allow for arbitrary code execution, this vulnerability enables untrusted users to impact the integrity and availability of the jupyter-server instance that was provisioned to them. The user already has access to their own single-user server's data, so installing an extension grants no new read access.

In particular, the integrity of data can be impacted, and any hardening or restrictions on permitted user actions (download/upload limits) within the single-user server can be circumvented. Availability impact on a JupyterHub deployment is limited: while a user can be expected to exhaust their own kernel pod's resources, this vulnerability makes it easier to also exhaust the single-user server resources or generate more requests to shared resources; where limits are absent, resource exhaustion could potentially degrade the wider deployment.

### Patches

JupyterLab [`v4.6.2`](https://github.com/jupyterlab/jupyterlab/releases/tag/v4.6.2) and [`v4.5.10`](https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.10) contain the patch.

Users of applications that depend on JupyterLab, such as Notebook v7+, should update `jupyterlab` package too.

### Workarounds

No action is required for deployments that do not have a custom allow/block list configured. Deployments wanting to disable programmatic extension installation entirely can switch to the read-only extension manager:

```bash
--LabApp.extension_manager=readonly
```

or the following traitlet:

```python
c.LabApp.extension_manager = 'readonly'
```

You can confirm that the read-only manager is in use from GUI:

<img width="293" height="293" alt="image" src="https://github.com/user-attachments/assets/8016c809-633e-4ed0-a5bc-6bc4793caa0f" />

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-89vp-jrxv-24w8
- https://github.com/jupyterlab/jupyterlab/pull/19184
- https://github.com/jupyterlab/jupyterlab/pull/19185
- https://github.com/jupyterlab/jupyterlab/pull/19186
- https://github.com/jupyterlab/jupyterlab/commit/be9303f5bcd5308eaeae953c5a3c903046682c2c
- https://github.com/jupyterlab/jupyterlab/commit/f1beab4a2027af4719d6edc07d52d6cf5a39a432
- https://github.com/jupyterlab/jupyterlab
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.10
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.6.2
