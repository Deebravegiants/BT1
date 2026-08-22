# [?] Merge #16878: Fix non-deterministic coverage of test DoS_mapOrphans

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-07-21
Source: https://github.com/litecoin-project/litecoin/commit/b763ae02a6601053156b3402c4409cc7c722b95d
Type: security-commit

## Details
Merge #16878: Fix non-deterministic coverage of test DoS_mapOrphans

4455949d6f0218b40d33d7fe6de6555f8f62192f Make test DoS_mapOrphans deterministic (David Reikher)

Pull request description:

  This pull request proposes a solution to make the test `DoS_mapOrphans` in denialofservice_tests.cpp have deterministic coverage.

  The `RandomOrphan` function in denialofservice_tests.cpp and the implicitly called function `ecdsa_signature_parse_der_lax` in pubkey.cpp were causing the non-deterministic test coverage.

  In the former, if a random orphan was selected the index of which is bigger than the max. orphan index in `mapOrphanTransactions`, the last orphan was returned from `RandomOrphan`. If the random number generated was never large enough, this condition would not be fulfilled and the corresponding branch wouldn't run. The proposed solution is to force one of the 50 dependant orphans to depend on the last orphan in `mapOrphanTransactions` using the newly introduced function `OrphanByIndex` (and passing it a large uint256), forcing this branch to run at least once.

  In the latter, if values for ECDSA `R` or `S` (or both) had no leading zeros, some code would not be executed. The solution was to find a constant signature that would be comprised of `R` and `S` values with leading zeros and calling `CPubKey::Verify` at the end of the test with this signature forcing this code to always run at least once at the end even if it hadn't throughout the test.

  To test that the coverage is (at least highly likely) deterministic, I ran

  `contrib/devtools/test_deterministic_coverage.sh denialofservice_tests/DoS_mapOrphans 1000`

  and the result was deterministic coverage across 1000 runs.

  Also - removed denialofservice_tests test entry from the list of non-deterministic tests in the coverage script.

ACKs for top commit:
  MarcoFalke:
    ACK 4455949d6f0218b40d33d7fe6de6555f8f62192f

Tree-SHA512: 987eb1f94b80d5bec4d4944e91ef43b9b8603055750362d4b4665b7f011be27045808aa9f4c6ccf8ae009b61405f9a1b8671d65a843c3328e5b8acce1f1c00a6
