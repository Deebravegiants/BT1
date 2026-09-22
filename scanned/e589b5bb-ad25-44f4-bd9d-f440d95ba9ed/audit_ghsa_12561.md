# [M] ink! vulnerable to incorrect decoding of storage value when using `DelegateCall`

## Summary
Severity: Medium
Advisory: GHSA-853p-5678-hv8f
CVE: CVE-2023-34449
CWE: CWE-253, CWE-754
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-853p-5678-hv8f
Type: github-advisory

## Affected
- crates.io: `ink` — affected >=4.0.0 <4.2.1
- crates.io: `ink_env` — affected >=4.0.0 <4.2.1

## Details
### Summary
The return value when using delegate call mechanics, either through [`CallBuilder::delegate`](https://docs.rs/ink_env/4.2.0/ink_env/call/struct.CallBuilder.html#method.delegate) or [`ink_env::invoke_contract_delegate`](https://docs.rs/ink_env/4.2.0/ink_env/fn.invoke_contract_delegate.html), is being decoded incorrectly.

### Description
Consider this minimal example:

```rust
// First contract, this will be performing a delegate call to the `Callee`.
#[ink(storage)]
pub struct Caller {
    value: u128,
}

#[ink(message)]
pub fn get_value(&self, callee_code_hash: Hash) -> u128 {
    let result = build_call::<DefaultEnvironment>()
        .delegate(callee_code_hash)
        .exec_input(ExecutionInput::new(Selector::new(ink::selector_bytes!(
            "get_value"
        ))))
        .returns::<u128>()
        .invoke();

    result
}

// Different contract, using this code hash for the delegate call.
#[ink(storage)]
pub struct Callee {
    value: u128,
}

#[ink(message)]
pub fn get_value(&self) -> u128 {
    self.value
}
```

In this example we are executing the `Callee` code in the context of the `Caller` contract. This means we'll be using the storage values of the `Caller` contract.

Running this code we expect the delegate call to return `value` as it was stored in the `Caller` contract. However, due to the reported bug a different value is returned (for the case of `uint`s it is `256` times the expected value).

### Impact
After conducting an analysis of the on-chain deployments of ink! contracts on Astar, Shiden, Aleph Zero, Amplitude and Pendulum, we have found that no contracts on those chains have been affected by the issue.

This bug was related to the mechanics around decoding a call's return buffer, which was changed as part of https://github.com/paritytech/ink/pull/1450. Since this feature was only released in ink! 4.0.0 no previous versions are affected.

### Mitigations
If you have an ink! 4.x series contract, please update it to the [4.2.1](https://github.com/paritytech/ink/releases/tag/v4.2.1) patch release that we just published. 

### Credits
Thank you Facundo Lerena from [CoinFabrik](https://www.coinfabrik.com) for reporting this problem in a well-structured and responsible way.

## References
- https://github.com/paritytech/ink/security/advisories/GHSA-853p-5678-hv8f
- https://nvd.nist.gov/vuln/detail/CVE-2023-34449
- https://github.com/paritytech/ink/pull/1450
- https://github.com/paritytech/ink/commit/f1407ee9f87e5f64d467a22d26ee88f61db7f3db
- https://docs.rs/ink_env/4.2.0/ink_env/call/struct.CallBuilder.html#method.delegate
- https://docs.rs/ink_env/4.2.0/ink_env/fn.invoke_contract_delegate.html
- https://github.com/paritytech/ink
