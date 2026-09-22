# [H] Trivy has a path traversal via a crafted vulnerability database or other downloaded artifacts

## Summary
Severity: High
Advisory: GHSA-mcj4-mphf-j9ff
CVE: CVE-2026-55092
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-mcj4-mphf-j9ff
Type: github-advisory

## Affected
- Go: `github.com/aquasecurity/trivy` — affected >=0 <0.71.1

## Details
## Summary

When Trivy downloads an OCI artifact, it uses the `org.opencontainers.image.title` annotation from the artifact manifest as the destination filename without validation. An attacker who can make Trivy fetch an attacker-controlled artifact can supply a crafted annotation that resolves to a path outside the intended destination, causing Trivy to write the layer content to an arbitrary location on the host filesystem.

## Affected configurations

Exploitation requires the attacker to direct Trivy at an attacker-controlled OCI artifact via one of the following inputs:

| Input | Used for |
| --- | --- |
| `--db-repository` flag, `TRIVY_DB_REPOSITORY` environment variable, or `db.repository` in `trivy.yaml` | Vulnerability database |
| `--java-db-repository` flag, `TRIVY_JAVA_DB_REPOSITORY` environment variable, or `db.java-repository` in `trivy.yaml` | Java vulnerability database |
| `--checks-bundle-repository` flag (and the deprecated `--policy-bundle-repository` alias), `TRIVY_CHECKS_BUNDLE_REPOSITORY` environment variable, or `misconfiguration.checks-bundle-repository` in `trivy.yaml` | Misconfiguration checks bundle |
| Repository argument to `trivy module install <REPO>` | WASM module installation |

Realistic scenarios in which an attacker may influence these inputs include a copy-pasted command or documentation snippet pointing to an untrusted mirror, or a third-party mirror that turns out to be hostile.

Trivy's default configuration, which downloads these artifacts from Aqua-operated repositories, is not affected. The risk applies only when one of the inputs above is overridden to download a different artifact.

## Impact

An attacker who satisfies the conditions above can overwrite or create arbitrary files on the host filesystem within the privilege boundary of the user running Trivy. The vulnerability does not grant any privileges beyond what that user already has.

The practical impact depends on the deployment. In environments where the running user can overwrite files such as SSH `authorized_keys`, shell startup files, cron entries, or binaries on `PATH`, the file write may be leveraged to achieve code execution as that user. In more restricted deployments, the impact is bounded to the user's writable scope but may still allow tampering with scan results, build artifacts, or other files consumed by subsequent steps in the same pipeline.

## Patches

Fixed in Trivy `0.71.1`. Users should upgrade to that release or later.

## Workarounds

If upgrading is not immediately possible, do not download Trivy artifacts (vulnerability database, Java database, misconfiguration checks bundle, modules, etc.) from OCI repositories you do not operate or trust.

## Credits

Reported by @ikkebr.

## References
- https://github.com/aquasecurity/trivy/security/advisories/GHSA-mcj4-mphf-j9ff
- https://nvd.nist.gov/vuln/detail/CVE-2026-55092
- https://github.com/aquasecurity/trivy/commit/39e0b132260c60d59fa746c3f6dd10374b0ff6e4
- https://github.com/aquasecurity/trivy/commit/a72d9a4d997c25fbb6534e231b4e206c9b202b31
- https://github.com/aquasecurity/trivy
- https://github.com/aquasecurity/trivy/releases/tag/v0.71.1
