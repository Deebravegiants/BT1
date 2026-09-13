# [H] Frontier opcode SUICIDE touches too many storage values on large contracts

## Summary
Severity: High
Advisory: CVE-2023-45130
Aliases: GHSA-gc88-2gvv-gp3v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-13
Source: https://osv.dev/vulnerability/CVE-2023-45130
Type: osv

## Details
Frontier is Substrate's Ethereum compatibility layer. Prior to commit aea528198b3b226e0d20cce878551fd4c0e3d5d0, at the end of a contract execution, when opcode SUICIDE marks a contract to be deleted, the software uses `storage::remove_prefix` (now renamed to `storage::clear_prefix`) to remove all storages associated with it. This is a single IO primitive call passing the WebAssembly boundary. For large contracts, the call (without providing a `limit` parameter) can be slow. In addition, for parachains, all storages to be deleted will be part of the PoV, which easily exceed relay chain PoV size limit. On the other hand, Frontier's maintainers only charge a fixed cost for opcode SUICIDE. The maintainers consider the severity of this issue high, because an attacker can craft a contract with a lot of storage values on a parachain, and then call opcode SUICIDE on the contract. If the transaction makes into a parachain block, the parachain will then stall because the PoV size will exceed relay chain's limit. This is especially an issue for XCM transactions, because they can't be skipped. Commit aea528198b3b226e0d20cce878551fd4c0e3d5d0 contains a patch for this issue. For parachains, it's recommended to issue an emergency runtime upgrade as soon as possible. For standalone chains, the impact is less severe because the issue mainly affects PoV sizes. It's recommended to issue a normal runtime upgrade as soon as possible. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45130.json
- https://github.com/paritytech/frontier/security/advisories/GHSA-gc88-2gvv-gp3v
- https://nvd.nist.gov/vuln/detail/CVE-2023-45130
- https://github.com/paritytech/frontier/commit/aea528198b3b226e0d20cce878551fd4c0e3d5d0
- https://github.com/paritytech/frontier/pull/1212
