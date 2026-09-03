# [?] Fix crash in `indy-node-control`

## Summary
Severity: Unknown
Chain: Hyperledger Indy
Component: hyperledger/indy-node
Published: 2022-03-29
Source: https://github.com/hyperledger-indy/indy-node/commit/88bbc1ff073437c51bfa62e29bad98d98daaf4fe
Type: security-commit

## Details
Fix crash in `indy-node-control`

- python3-pygments and python3-intervaltree do not exist as dependencies in plenum anymore.
- The `indy-node-control` crashes when trying to hold packages that don't exist.
- Fixes the issue found here; https://github.com/hyperledger/indy-test-automation/issues/113

Signed-off-by: Wade Barnes <wade@neoterictech.ca>
