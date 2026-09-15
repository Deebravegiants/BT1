# [C] Server-Side Request Forgery in FlyteConsole

## Summary
Severity: Critical
Advisory: CVE-2022-24856
Aliases: GHSA-www6-hf2v-v9m9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-05-17
Source: https://osv.dev/vulnerability/CVE-2022-24856
Type: osv

## Details
FlyteConsole is the web user interface for the Flyte platform. FlyteConsole prior to version 0.52.0 is vulnerable to server-side request forgery (SSRF) when FlyteConsole is open to the general internet. An attacker can exploit any user of a vulnerable instance to access the internal metadata server or other unauthenticated URLs. Passing of headers to an unauthorized actor may occur. The patch for this issue deletes the entire `cors_proxy`, as this is not required for console anymore. A patch is available in FlyteConsole version 0.52.0. Disable FlyteConsole availability on the internet as a workaround.

## References
- https://github.com/flyteorg/flyteconsole/releases/tag/v0.52.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24856.json
- https://github.com/flyteorg/flyteconsole/security/advisories/GHSA-www6-hf2v-v9m9
- https://nvd.nist.gov/vuln/detail/CVE-2022-24856
- https://github.com/flyteorg/flyteconsole/commit/05b88ed2d2ecdb5d8a8404efea25414e57189709
- https://github.com/flyteorg/flyteconsole/pull/389
