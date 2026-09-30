# [H] Wasmi Out-of-bounds Write for host to Wasm calls with more than 128 Parameters

## Summary
Severity: High
Advisory: GHSA-75jp-vq8x-h4cq
CVE: CVE-2024-28123
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-07
Source: https://github.com/advisories/GHSA-75jp-vq8x-h4cq
Type: github-advisory

## Affected
- crates.io: `wasmi` — affected >=0.15.0 <0.31.1

## Details
### Summary

In the WASMI Interpreter, an [Out-of-bounds Buffer Write](https://cwe.mitre.org/data/definitions/787.html) will arise arise if the host calls or resumes a Wasm function with more parameters than the default limit (128), as it will surpass the stack value. This doesn’t affect calls from Wasm to Wasm, only from host to Wasm.

### Impact

After conducting an analysis of the dependent Polkadot systems of `wasmi`: [Pallet Contracts](https://github.com/paritytech/polkadot-sdk/tree/master/substrate/frame/contracts), [Parity Signer](https://github.com/paritytech/parity-signer), and [Smoldot](https://github.com/smol-dot/smoldot), we have found that none on those systems have been affected by the issue as they are calling host to Wasm function with a small limited amount of parameters always. 

### Mitigations

If you are using `wasmi` betwen version 0.15.0 and 0.31.0, please update it to the [0.31.1](https://github.com/paritytech/wasmi/releases/tag/v0.31.1) patch release that we just published.

### Workarounds

Ensure no more than 128 parameters can be pass in a call from the host to a Wasm function. 

### References

Patch PR: <PR>

### Special thanks

Special thanks to Stellar Development Foundation for reporting this security vulnerability.

## References
- https://github.com/wasmi-labs/wasmi/security/advisories/GHSA-75jp-vq8x-h4cq
- https://nvd.nist.gov/vuln/detail/CVE-2024-28123
- https://github.com/wasmi-labs/wasmi/commit/f7b3200e9f3dc9e2cbca966cb255c228453c792f
- https://github.com/wasmi-labs/wasmi
- https://github.com/wasmi-labs/wasmi/releases/tag/v0.31.1
