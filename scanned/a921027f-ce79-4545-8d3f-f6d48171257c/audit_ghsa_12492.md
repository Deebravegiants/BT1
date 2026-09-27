# [H] Candid infinite decoding loop through specially crafted payload

## Summary
Severity: High
Advisory: GHSA-7787-p7x6-fq3j
CVE: CVE-2023-6245
CWE: CWE-1288, CWE-400, CWE-835
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-7787-p7x6-fq3j
Type: github-advisory

## Affected
- crates.io: `candid` — affected >=0.9.0 <0.9.10

## Details
### Impact

The Candid library causes a Denial of Service while parsing a specially crafted payload with `empty` data type. For example, if the payload is `record { * ; empty }` and  the canister interface expects `record { * }` then the rust candid decoder treats `empty` as an extra field required by the type.  The problem with type `empty` is that the candid rust library wrongly categorizes `empty` as a recoverable error when skipping the field and thus causing an infinite decoding loop. 

Canisters using affected versions of candid are exposed to denial of service by causing the decoding to run indefinitely until the canister traps due to reaching maximum instruction limit per execution round. Repeated exposure to the payload will result in degraded performance of the canister.

For asset canister users, `dfx` versions `>= 0.14.4` to `<= 0.15.2-beta.0` ships asset canister with an affected version of candid.

#### Unaffected 
- Rust canisters using candid `< 0.9.0` or `>= 0.9.10` 
- Rust canister interfaces of type other than `record { * }`
- Motoko based canisters
- dfx (for asset canister) `<= 0.14.3` or `>= 0.15.2`


### Patches

The issue has been patched in `0.9.10`. All rust based canisters on candid versions `>= 0.9.0` must upgrade their candid versions to `>= 0.9.10` and deploy their canisters to mainnet as soon as possible. 

### Workarounds

There is no workaround for canisters using the affected versions of candid other than upgrading to patched version.

### References
-  [dfinity/candid/pull/478](https://github.com/dfinity/candid/pull/478)
-  [Candid Library Reference](https://internetcomputer.org/docs/current/references/candid-ref)
-  [Candid Specification](https://github.com/dfinity/candid/blob/master/spec/Candid.md)
-  [Internet Computer Specification](https://internetcomputer.org/docs/current/references/ic-interface-spec)

## References
- https://github.com/dfinity/candid/security/advisories/GHSA-7787-p7x6-fq3j
- https://nvd.nist.gov/vuln/detail/CVE-2023-6245
- https://github.com/dfinity/candid/pull/478
- https://github.com/dfinity/candid/commit/b233dbc2d2bcc79c9fc574dd5968269df680b073
- https://github.com/dfinity/candid
- https://github.com/dfinity/candid/blob/master/spec/Candid.md
- https://internetcomputer.org/docs/current/references/candid-ref
- https://internetcomputer.org/docs/current/references/ic-interface-spec
- https://rustsec.org/advisories/RUSTSEC-2023-0073.html
