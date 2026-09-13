# [M] Control character injection in console output in github.com/ipfs/go-ipfs 

## Summary
Severity: Medium
Chain: github.com/ipfs/go-ipfs
Component: github.com/ipfs/go-ipfs
CVE: CVE-2020-26283
CWE: Improper Encoding or Escaping of Output, Improper Neutralization of Escape, Meta, or Control Sequences
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-r4gv-vj59-cccm
Type: github-advisory

## Details
### Impact
Control characters are not escaped from console output. This can result in hiding input from the user which could result in the user taking an unknown, malicious action.

### Patches
<!-- _Has the problem been patched? What versions should users upgrade to?_  -->

- Patched via https://github.com/ipfs/go-ipfs/pull/7831 in v0.8.0

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [go-ipfs](http://github.com/ipfs/go-ipfs)
* Email us at [security@ipfs.io](mailto:security@ipfs.io)
