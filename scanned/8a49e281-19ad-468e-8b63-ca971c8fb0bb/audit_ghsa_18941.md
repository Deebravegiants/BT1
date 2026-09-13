# [H] Grype has a credential disclosure vulnerability in its JSON output

## Summary
Severity: High
Advisory: GHSA-6gxw-85q2-q646
CVE: CVE-2025-65965
CWE: CWE-212
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-6gxw-85q2-q646
Type: github-advisory

## Affected
- Go: `github.com/anchore/grype` — affected >=0.68.0 <0.104.1

## Details
A credential disclosure vulnerability was found in Grype, affecting versions `v0.68.0` through `v0.104.0`. If registry credentials are defined and the output of grype is written using the `--file` or `--output json=<file>` option, the registry credentials will be included unsanitized in the output file.

## Impact

In Grype versions `v0.68.0` through `v0.104.0`, when registry authentication is configured, those credentials can be incorrectly included in the output of a Grype scan (regardless of whether those credentials are actively being used for the current scan). Users that do not have registry authentication configured are not affected by this issue.

Registry credentials can be set via the Grype configuration file (e.g. `registry.auth[].username`, `registry.auth[].password`, `registry.auth[].token`) or environment variables (e.g., `GRYPE_REGISTRY_AUTH_USERNAME`, `GRYPE_REGISTRY_AUTH_PASSWORD`, `GRYPE_REGISTRY_AUTH_TOKEN`).

In order for the authentication details to be improperly included, the Grype file output format must be set to `json` with output target set to a file. For example `--output json=file.json` or `--output json --file file.json`. When these conditions are met, the configured credentials are not sanitized as they should be in the resulting JSON output file.

The authentication details could also be leaked via a malformed Grype Template. A Grype Template that includes the `Descriptor.Registry.Auth` fields would also include the unsanitized registry credentials. There are no known templates that include these fields.

## Patches
The patch has been released in `v0.104.1`.

## Workaround
Users running affected versions of grype can work around this vulnerability by redirecting stdout to a file instead of using the `--file` or `--output` options.

For example, replacing the command:

```
# using `--output json=path` (or `--file`) leaks credentials
grype --output json=test.json alpine:latest
```

with

```
# no use of `--output json=path` or `--file`. Output is sanitized...
grype --output json alpine:latest > test.json
```

...results in the same `test.json` output, but the credentials will be properly sanitized.

## Resources
Patch pull request: https://github.com/anchore/grype/pull/3068

## References
- https://github.com/anchore/grype/security/advisories/GHSA-6gxw-85q2-q646
- https://nvd.nist.gov/vuln/detail/CVE-2025-65965
- https://github.com/anchore/grype/pull/3068
- https://github.com/anchore/grype/commit/39f7fa17af2739cafe9b27176d4a68f7c05f21c1
- https://github.com/anchore/grype/commit/c99f79de49a58dc16d7fd8f35160b169b87db9de
- https://github.com/anchore/grype
