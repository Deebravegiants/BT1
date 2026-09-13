# [M] EVerest: Charging Continues When WithdrawAuthorization Is Processed Before TransactionStarted

## Summary
Severity: Medium
Advisory: CVE-2026-29044
Aliases: GHSA-gx37-p775-qf5v
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-29044
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2026.02.0, when WithdrawAuthorization is processed before the TransactionStarted event, AuthHandler determines `transaction_active=false` and only calls `withdraw_authorization_callback`. This path ultimately calls `Charger::deauthorize()`, but no actual stop (StopTransaction) occurs in the Charging state. As a result, authorization withdrawal can be defeated by timing, allowing charging to continue. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29044.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-gx37-p775-qf5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-29044
