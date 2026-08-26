# [?] service.head race condition fix (#10741)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2022-05-27
Source: https://github.com/OffchainLabs/prysm/commit/adabd1fa4f9acf356a5ce06a4f0fe391db174037
Type: security-commit

## Details
service.head race condition fix (#10741)

* added various read mutex locks for service.head

* added RLocks around all calls to s.headRoot()

* added RLocks around all calls to s.headBlock()

* reduce lock surface-> Stop(),handleEpochBoundary()

* refactor Stop() to +performance, -lock_surface

* Apply suggestions from code review

Co-authored-by: terencechain <terence@prysmaticlabs.com>

* fixed indentation

Co-authored-by: terencechain <terence@prysmaticlabs.com>
Co-authored-by: Raul Jordan <raul@prysmaticlabs.com>
Co-authored-by: Radosław Kapka <rkapka@wp.pl>
