# [?] [fix] #1480: Shut down on panic (#2445)

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger/iroha
Published: 2022-07-07
Source: https://github.com/hyperledger-iroha/iroha/commit/2c897f23f95e04d2a61077729b1ffef847acc199
Type: security-commit

## Details
[fix] #1480: Shut down on panic (#2445)

* [fix] #1480: Add panic hook to exit program on panic

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #1480: Use quit crate instead of process::exit

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #1480: Use tokio::Notify

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #1480: Update test

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #1480: Fix linter issues

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>
