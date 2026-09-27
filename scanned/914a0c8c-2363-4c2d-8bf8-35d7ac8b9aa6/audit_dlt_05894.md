# [?] Run vulnerability scan on latest release tags

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2025-02-14
Source: https://github.com/hyperledger/fabric/commit/f07477bb8b48f387c5d7dd15361c4df99f521da4
Type: security-commit

## Details
Run vulnerability scan on latest release tags

Vulnerability scans were previously run only on the latest state of
currently developed branches. This provided assurance that the current
branch state did not contain known vulnerabilities in dependencies, but
did not provide assurance that the currently released code was free of
vulnerabilities.

This change runs additional vulnerability scans on the most recent
release version tag for currently developed branches. Scan failures now
indicate that a new release is required to address vulnerabilities in
dependencies.

Signed-off-by: Mark S. Lewis <Mark.S.Lewis@outlook.com>
