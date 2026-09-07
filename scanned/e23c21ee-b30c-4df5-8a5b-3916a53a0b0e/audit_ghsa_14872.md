# [M] Docker CLI leaks private registry credentials to registry-1.docker.io

## Summary
Severity: Medium
Advisory: GHSA-99pg-grm5-qq3v
CVE: CVE-2021-41092
CWE: CWE-200, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-99pg-grm5-qq3v
Type: github-advisory

## Affected
- Go: `github.com/docker/cli` — affected >=0 <20.10.9

## Details
## Impact

A bug was found in the Docker CLI where running `docker login my-private-registry.example.com` with a misconfigured configuration file (typically `~/.docker/config.json`) listing a `credsStore` or `credHelpers` that could not be executed would result in any provided credentials being sent to `registry-1.docker.io` rather than the intended private registry.

## Patches

This bug has been fixed in Docker CLI 20.10.9.  Users should update to this version as soon as possible.

## Workarounds

Ensure that any configured `credsStore` or `credHelpers` entries in the configuration file reference an installed credential helper that is executable and on the `PATH`.

## For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/docker/cli/issues/new/choose)
* Email us at security@docker.com if you think you’ve found a security bug

## References
- https://github.com/docker/cli/security/advisories/GHSA-99pg-grm5-qq3v
- https://nvd.nist.gov/vuln/detail/CVE-2021-41092
- https://github.com/docker/cli/commit/893e52cf4ba4b048d72e99748e0f86b2767c6c6b
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B5Q6G6I4W5COQE25QMC7FJY3I3PAYFBB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZNFADTCHHYWVM6W4NJ6CB4FNFM2VMBIB
