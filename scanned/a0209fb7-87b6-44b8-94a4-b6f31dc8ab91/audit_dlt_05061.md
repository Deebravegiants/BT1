# [H] Snappy decompress length can be very large and causes out of memory error 

## Summary
Severity: High
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2020-08-12
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-3gjh-29fv-8hr6
Type: github-advisory

## Details
### Impact

Adversary can create message which compressed size is less than the package limit but the decompressed length is very large such as 1G. It will cost the node many memories to process the network messages, and on the system with less than 1G memory, the process is killed directly because of out of memory error.

### Patches

The node must check the decompress length before allocating the memory for the message.

### References

* https://github.com/nervosnetwork/ckb/blob/687d797f1888dd05d1f38ce6d1bef3e5b9b6e38b/network/src/compress.rs#L68
* https://github.com/BurntSushi/rust-snappy/blob/master/src/decompress.rs#L106
* https://github.com/BurntSushi/rust-snappy/blob/6cfb836463b9b3ac48ca7cd15d0a50d030e95769/src/decompress.rs#L30
