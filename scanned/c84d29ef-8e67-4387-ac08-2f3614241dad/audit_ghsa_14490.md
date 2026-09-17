# [C] angular-server-side-configuration information disclosure vulnerability in monorepo with node.js backend

## Summary
Severity: Critical
Advisory: GHSA-gwvm-vrp4-4pp5
CVE: CVE-2023-28444
CWE: CWE-200, CWE-538
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-gwvm-vrp4-4pp5
Type: github-advisory

## Affected
- npm: `angular-server-side-configuration` — affected >=15.0.0 <15.1.0

## Details
### Impact
angular-server-side-configuration detects used environment variables in TypeScript (.ts) files during build time of an Angular CLI project. The detected environment variables are written to a ngssc.json file in the output directory.
During deployment of an Angular based app, the environment variables based on the variables from ngssc.json are inserted into the apps index.html (or defined index file).

With version 15 the environment variable detection was widened to the entire project, relative to the angular.json file from the Angular CLI. In a monorepo setup, this could lead to environment variables intended for a backend/service to be detected and written to the ngssc.json, which would then be populated and exposed via index.html.

This has NO IMPACT, in a plain Angular project that has no backend component.

### Patches
Vulnerability has been mitigated in 15.1.0, by adding an option `searchPattern` which restricts the detection file range by default.

```bash
# Update via npm
npm update angular-server-side-configuration
## Or more specific
npm install angular-server-side-configuration@15.1.0

# Update via pnpm
pnpm update angular-server-side-configuration
## Or more specific
pnpm add angular-server-side-configuration@15.1.0

# Update via yarn
yarn update angular-server-side-configuration
## Or more specific
yarn add angular-server-side-configuration@15.1.0
```

### Workarounds
Manually edit or create ngssc.json or run a script after ngssc.json generation

### References

## References
- https://github.com/kyubisation/angular-server-side-configuration/security/advisories/GHSA-gwvm-vrp4-4pp5
- https://nvd.nist.gov/vuln/detail/CVE-2023-28444
- https://github.com/kyubisation/angular-server-side-configuration/commit/d701f51260637a84ede278e248934e0437a7ff86
- https://github.com/kyubisation/angular-server-side-configuration
- https://github.com/kyubisation/angular-server-side-configuration/releases/tag/v15.1.0
