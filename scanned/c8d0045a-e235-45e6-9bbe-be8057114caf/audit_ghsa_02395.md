# [C] remote code execution via git repo provider

## Summary
Severity: Critical
Advisory: GHSA-9jjr-qqfp-ppwx
CVE: CVE-2021-39159
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-9jjr-qqfp-ppwx
Type: github-advisory

## Affected
- PyPI: `binderhub` — affected >=0 <0.2.0

## Details
### Impact

A remote code execution vulnerability has been identified in BinderHub, where providing BinderHub with maliciously crafted input could execute code in the BinderHub context, with the potential to egress credentials of the BinderHub deployment, including JupyterHub API tokens, kubernetes service accounts, and docker registry credentials. This may provide the ability to manipulate images and other user created pods in the deployment, with the potential to escalate to the host depending on the underlying kubernetes configuration.

### Patches

Patch below, or [on GitHub](https://github.com/jupyterhub/binderhub/commit/195caac172690456dcdc8cc7a6ca50e05abf8182.patch)

```diff
From 9f4043d9dddc1174920e687773f27b7933f48ab6 Mon Sep 17 00:00:00 2001
From: Riccardo Castellotti <rcastell@cern.ch>
Date: Thu, 19 Aug 2021 15:49:43 +0200
Subject: [PATCH] Explicitly separate git-ls-remote options from positional
 arguments

---
 binderhub/repoproviders.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

diff --git a/binderhub/repoproviders.py b/binderhub/repoproviders.py
index f33347b..5d4b87c 100755
--- a/binderhub/repoproviders.py
+++ b/binderhub/repoproviders.py
@@ -484,7 +484,7 @@ class GitRepoProvider(RepoProvider):
             self.sha1_validate(self.unresolved_ref)
         except ValueError:
             # The ref is a head/tag and we resolve it using `git ls-remote`
-            command = ["git", "ls-remote", self.repo, self.unresolved_ref]
+            command = ["git", "ls-remote", "--", self.repo, self.unresolved_ref]
             result = subprocess.run(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
             if result.returncode:
                 raise RuntimeError("Unable to run git ls-remote to get the `resolved_ref`: {}".format(result.stderr))
-- 
2.25.1

```

### Workarounds

Disable the git repo provider by specifying the `BinderHub.repo_providers` config, e.g.:

```python
from binderhub.repoproviders import (GitHubRepoProvider,
                            GitLabRepoProvider, GistRepoProvider,
                            ZenodoProvider, FigshareProvider, HydroshareProvider,
                            DataverseProvider)

c.BinderHub.repo_providers =  {
            'gh': GitHubRepoProvider,
            'gist': GistRepoProvider,
            'gl': GitLabRepoProvider,
            'zenodo': ZenodoProvider,
            'figshare': FigshareProvider,
            'hydroshare': HydroshareProvider,
            'dataverse': DataverseProvider,
        }
```

### References

Credit: Jose Carlos Luna Duran (CERN) and Riccardo Castellotti (CERN).

### For more information

If you have any questions or comments about this advisory:

* Email us at [security@ipython.org](mailto:security@ipython.org)

## References
- https://github.com/jupyterhub/binderhub/security/advisories/GHSA-9jjr-qqfp-ppwx
- https://nvd.nist.gov/vuln/detail/CVE-2021-39159
- https://github.com/jupyterhub/binderhub/commit/195caac172690456dcdc8cc7a6ca50e05abf8182
- https://github.com/jupyterhub/binderhub/commit/195caac172690456dcdc8cc7a6ca50e05abf8182.patch
- https://github.com/jupyterhub/binderhub
- https://github.com/pypa/advisory-database/tree/main/vulns/binderhub/PYSEC-2021-371.yaml
