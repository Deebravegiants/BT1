# [M] Alchemy's Modular Account can use executeUserOp to bypass allowlist prevalidation hook

## Summary
Severity: Medium
Advisory: CVE-2025-46834
Aliases: GHSA-jhp7-7cq9-m4pv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-05-15
Source: https://osv.dev/vulnerability/CVE-2025-46834
Type: osv

## Details
Alchemy's Modular Account is a smart contract account that is compatible with ERC-4337 and ERC-6900. In versions on the 2.x branch prior to commit 5e6f540d249afcaeaf76ab95517d0359fde883b0, owners of Modular Accounts can grant session keys (scoped external keys) to external parties and would use the allowlist module to restrict which external contracts can be accessed by the session key. There is a bug in the allowlist module in that we don't check for the `executeUserOp` -> `execute` or `executeBatch` path, effectively allowing any session key to bypass any access control restrictions set on the session key. Session keys are able to access ERC20 and ERC721 token contracts amongst others, transferring all tokens from the account out andonfigure the permissions on external modules on session keys. They would be able to remove all restrictions set on themselves this way, or rotate the keys of other keys with higher privileges into keys that they control. Commit 5e6f540d249afcaeaf76ab95517d0359fde883b0 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46834.json
- https://github.com/alchemyplatform/modular-account/security/advisories/GHSA-jhp7-7cq9-m4pv
- https://nvd.nist.gov/vuln/detail/CVE-2025-46834
- https://github.com/alchemyplatform/modular-account/commit/5e6f540d249afcaeaf76ab95517d0359fde883b0
