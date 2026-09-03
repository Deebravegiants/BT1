# [C] Arbitrary code execution in guest via memory safety failure in `sys_read`

## Summary
Severity: Critical
Chain: ZK
Component: risc0/risc0
CVE: CVE-2025-61588
Published: 2025-10-01
Source: https://github.com/risc0/risc0/security/advisories/GHSA-jqq4-c7wq-36h7
Type: github-advisory

## Details
# Arbitrary code execution in guest via memory safety failure in `sys_read`

In affected versions of `risc0-zkvm-platform`, when the zkVM guest calls `sys_read`, the host is able to use a crafted response to write to an arbitrary memory location in the guest. This capability can be leveraged to execute arbitrary code within the guest. As `sys_read` is the mechanism by which input is requested by the guest, all guest programs built with the affected versions are vulnerable. This critically compromises the soundness guarantees of the guest program.

A fix was applied in [\#3351](https://github.com/risc0/risc0/pull/3351). The vulnerable pointer arithmetic was removed, and replaced with a simplified implementation in the `v1compat` kernel which uses Rust’s slice functions to guarantee memory safety.

The fix has been released as part of `risc0-zkvm` versions `2.3.2` and `3.0.3`. All prior versions are affected.

## Remediation

All developers of zkVM applications should update their guests to use `risc0-zkvm` versions `^2.3.2` or `^3.0.3`.

This upgrade can be accomplished by editing all `Cargo.toml` files in the following way.

* Any references to [`risc0-zkvm`](https://crates.io/crates/risc0-zkvm) should use version specifiers `”2.3.2”` or `”3.0.3”`.  
* Any references to [`risc0-build`](https://crates.io/crates/risc0-build) should use version specifiers `”2.3.2”` or `”3.0.3”`, matching `risc0-zkvm`.  
* Any references to [`risc0-zkvm-platform`](https://crates.io/crates/risc0-zkvm-platform) should use version specifier `”2.1.0”` or later. Most projects will not have direct references to this crate.

Rebuild your application including the guest. You can run the following command to check that the patch is applied:

```shell
# Provide the path to your guest Cargo.toml. Should report risc0-zkvm-platform >=v2.1.0
cargo tree --depth 0 -p risc0-zkvm-platform --manifest-path path/to/methods/guest/Cargo.toml
```

Any applications that use the image ID of this guest need to be updated with the newly built image ID.

Note that there are no changes to the RISC Zero proof system or circuits. Provers are not required to take any action. Users of the Groth16 smart contract verifier and the [RISC Zero Verifier Router](https://dev.risczero.com/api/blockchain-integration/contracts/verifier#verifier-router) are not required to take any action beyond updating their guest programs.

Any applications using the `risc0-aggregation` crate or the `RiscZeroSetVerifier` smart contract should update to version `>=0.9`. This application includes a zkVM guest, which is vulnerable in versions prior to `0.9`. Instances of the `RiscZeroSetVerifier` operated by RISC Zero have been disabled via the estop mechanism outlined in the [Verifier Management Design](https://github.com/risc0/risc0-ethereum/blob/release-2.0/contracts/version-management-design.md#base-verifier-implementations).
