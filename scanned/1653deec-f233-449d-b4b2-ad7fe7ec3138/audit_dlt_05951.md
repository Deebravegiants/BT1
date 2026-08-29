# [?] Merge pull request from GHSA-7vrm-3jc8-5wwm

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-04-02
Source: https://github.com/vyperlang/vyper/commit/2c73f8352635c0a433423a5b94740de1a118e508
Type: security-commit

## Details
Merge pull request from GHSA-7vrm-3jc8-5wwm

* add more tests for string comparison

explicitly test the codepath with <= 32 bytes

* refactor keccak256 helper a bit

* fix bytestring equality

existing bytestring equality checks do not check length equality or for
dirty bytes.
