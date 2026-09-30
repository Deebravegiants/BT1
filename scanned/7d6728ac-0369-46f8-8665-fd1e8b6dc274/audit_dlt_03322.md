# [H] Panics as error-handling

## Summary
Severity: High
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-08
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/20
Type: code-finding

## Details
# Handle

nascent


# Vulnerability details

# [H-04] Panics as error-handling
**Severity: High**
**Likelihood: Medium**

The use of `.unwrap()`, `expect()`, and `assert!()` should be limited to tests, compile-time assertions (e.g. `const`s), and configuration checks. Panicks are at the thread level, so stopping one thread unexpectedly could cause undefined behavior in others. This can become a system-wide vulnerability when the panic can occur from reading the state of a contract due to it affecting all running daemons. Additionally, some of these unwraps, expects and asserts occur based off contract log output. Given how resyncing works, its possible for these panics to persist across process lifetimes (i.e. spin-up, crash, spin-up, crash...) resulting in a patch being required before the bridge returns to an operational state. 

## Recommendation
Wherever possible, replace instances of `unwrap()`, `expect()`, and `assert!()` with a `Result::Err()`.  Where necessary, change function signatures to return a `Result<>` and handle error cases at the highest level of execution, even if this means intentionally throwing away a result:

```Rust
let _res : Result<_, _> = func_that_can_fail();
```

or, ideally, logging any error condition

```Rust
if let Err(e) = func_that_canfail() {
    log!("error");
}
```
