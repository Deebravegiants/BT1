# [M] Credential disclosure in syft when SYFT_ATTEST_PASSWORD environment variable set

## Summary
Severity: Medium
Advisory: GHSA-jp7v-3587-2956
CVE: CVE-2023-24827
CWE: CWE-200, CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-jp7v-3587-2956
Type: github-advisory

## Affected
- Go: `github.com/anchore/syft` — affected >=0.69.0 <0.70.0

## Details
A password disclosure flaw was found in Syft versions v0.69.0 and v0.69.1. This flaw leaks the password stored in the SYFT_ATTEST_PASSWORD environment variable.

### Impact
The `SYFT_ATTEST_PASSWORD` environment variable is for the `syft attest` command to generate attested SBOMs for the given container image. This environment variable is used to decrypt the private key (provided with `syft attest --key <path-to-key-file>`)  during the signing process while generating an SBOM attestation. 

This vulnerability affects users running syft that have the `SYFT_ATTEST_PASSWORD` environment variable set with credentials (regardless of if the attest command is being used or not). Users that do not have the environment variable `SYFT_ATTEST_PASSWORD` set are not affected by this issue.

The credentials are leaked in two ways:
- in the syft logs when `-vv` or `-vvv` are used in the syft command (which is any log level >= `DEBUG`)
- in the attestation or SBOM only when the `syft-json` format is used 

Note that as of v0.69.0 any generated attestations by the `syft attest` command are uploaded to the OCI registry (if you have write access to that registry) in the same way `cosign attach` is done. This means that any attestations generated for the affected versions of syft when the `SYFT_ATTEST_PASSWORD` environment variable was set would leak credentials in the attestation payload uploaded to the OCI registry.

Example commands run from affected versions of syft that show the credential disclosure:
```bash
$ SYFT_ATTEST_PASSWORD=123456 syft <container-image-or-directory-input> -o syft-json | grep 123456
# "123456" is in the output

$ SYFT_ATTEST_PASSWORD=123456 syft attest <container-image-input> -o syft-json 
$ cosign download attestation <container-image-input> | jq -r '.payload' | base64 -d | grep 123456
# "123456" is in the output
```

### Patches

The patch has been released in v0.70.0.

### Workarounds

There are no workarounds for this vulnerability.

### References

Patch pull request: https://github.com/anchore/syft/pull/1538

## References
- https://github.com/anchore/syft/security/advisories/GHSA-jp7v-3587-2956
- https://nvd.nist.gov/vuln/detail/CVE-2023-24827
- https://github.com/anchore/syft/commit/9995950c70e849f9921919faffbfcf46401f71f3
- https://github.com/anchore/syft
