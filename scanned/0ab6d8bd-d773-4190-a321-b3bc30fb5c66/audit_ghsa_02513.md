# [M] Attack on Kubernetes via Misconfigured Argo Workflows

## Summary
Severity: Medium
Advisory: GHSA-rc7p-gmvh-xfx2
Ecosystem: Go
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-rc7p-gmvh-xfx2
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows` — affected >=0

## Details
### Impact

Users running using the Argo Server with `--auth-mode=server` (which is the default < v3.0.0) AND have exposed their UI to the Internet may allow remote users to execute arbitrary code on their cluster, e.g. crypto-mining.

### Resolution

* Do not expose your user interface to the Internet. 
* Change configuration. `--auth-mode=client`. 

For users using an older 2.x version of Argo Server, consider upgrading to Argo Server version 3.x or later.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-rc7p-gmvh-xfx2
- https://www.intezer.com/blog/container-security/new-attacks-on-kubernetes-via-misconfigured-argo-workflows
