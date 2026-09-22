# [?] cmd/geth: implement vulnerability check (#21859)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-12-04
Source: https://github.com/celo-org/celo-blockchain/commit/15339cf1c9af2b1242c2574869fa7afca1096cdf
Type: security-commit

## Details
cmd/geth: implement vulnerability check (#21859)

* cmd/geth: implement vulnerability check

* cmd/geth: use minisign to verify vulnerability feed

* cmd/geth: add the test too

* cmd/geth: more minisig/signify testing

* cmd/geth: support multiple pubfiles for signing

* cmd/geth: add @holiman minisig pubkey

* cmd/geth: polishes on vulnerability check

* cmd/geth: fix ineffassign linter nit

* cmd/geth: add CVE to version check struct

* cmd/geth/testdata: add missing testfile

* cmd/geth: add more keys to versionchecker

* cmd/geth: support file:// URLs in version check

* cmd/geth: improve key ID printing when signature check fails

Co-authored-by: Felix Lange <fjl@twurst.com>
