# [H] Backstage Scaffolder plugin has insecure sandbox

## Summary
Severity: High
Advisory: GHSA-wg6p-jmpc-xjmr
CVE: CVE-2023-35926
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-wg6p-jmpc-xjmr
Type: github-advisory

## Affected
- npm: `@backstage/plugin-scaffolder-backend` — affected >=0 <1.15.0

## Details
The Backstage scaffolder-backend plugin uses a templating library that requires a sandbox, as it by design allows for code injection. The library used for this sandbox so far has been `vm2`, but in light of several past vulnerabilities and existing vulnerabilities  that may not have a fix, the plugin has switched to using a different sandbox library.

### Impact

A malicious actor with write access to a registered scaffolder template could manipulate the template in a way that allows for remote code execution on the scaffolder-backend instance. This was only exploitable in the template YAML definition itself and not by user input data.

### Patches

This is vulnerability is fixed in version 1.15.0 of `@backstage/plugin-scaffolder-backend`.

### Workarounds

Note that the [Backstage Threat Model](https://backstage.io/docs/overview/threat-model) states that scaffolder templates are considered to be a sensitive area that with the recommendation that you control access and perform manual reviews of changes to the scaffolder templates. The exploit is of a nature where it is easily discoverable in manual review.

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-wg6p-jmpc-xjmr
- https://nvd.nist.gov/vuln/detail/CVE-2023-35926
- https://github.com/backstage/backstage/commit/fb7375507d56faedcb7bb3665480070593c8949a
- https://github.com/backstage/backstage
- https://github.com/backstage/backstage/releases/tag/v1.15.0
