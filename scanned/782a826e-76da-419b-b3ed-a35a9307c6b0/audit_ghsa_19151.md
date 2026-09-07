# [M] `gh attestation verify` returns incorrect exit code during verification if no attestations are present

## Summary
Severity: Medium
Advisory: GHSA-fgw4-v983-mgp8
CVE: CVE-2025-25204
CWE: CWE-390
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-fgw4-v983-mgp8
Type: github-advisory

## Affected
- Go: `github.com/cli/cli/v2` — affected >=2.49.0 <2.67.0

## Details
### Summary

A bug in GitHub's Artifact Attestation CLI tool, `gh attestation verify`, may return an incorrect zero exit status when no matching attestations are found for the specified `--predicate-type <value>` or the default `https://slsa.dev/provenance/v1` if not specified. This issue only arises if an artifact has an attestation with a predicate type different from the one provided in the command. As a result, users relying solely on these exit codes may mistakenly believe the attestation has been verified, despite the absence of an attestation with the specified predicate type and the tool printing a verification failure.

Users are advised to update `gh` to version `v2.67.0` as soon as possible.

Initial report: https://github.com/cli/cli/issues/10418
Fix: https://github.com/cli/cli/pull/10421

### Details

The gh attestation verify command fetches, loads, and attempts to verify attestations associated with a given artifact for a specified predicate type. If an attestation is found, but the predicate type does not match the one specified in the `gh attestation verify` command, the verification fails, but the program exits early.

Due to a re-used uninitialized error variable, when no matching attestations are found, the relevant function returns `nil` instead of an error, causing the program to exit with a status code of `0`, which incorrectly suggests successful verification.

### PoC

Run `gh attestation verify` with local attestations using the `--bundle` flag and specify a predicate type with `--predicate-type` that you know will not match any of the attestations the command will attempt to verify. Confirm that the command exits with a zero status code.

### Impact

Users who rely exclusively on the exit status code of `gh attestation verify` may incorrectly verify an attestation when the attestation's predicate type does not match the specified predicate type in the command.

## References
- https://github.com/cli/cli/security/advisories/GHSA-fgw4-v983-mgp8
- https://nvd.nist.gov/vuln/detail/CVE-2025-25204
- https://github.com/cli/cli/issues/10418
- https://github.com/cli/cli/pull/10421
- https://github.com/cli/cli
