# [M] diboot-core Authenticated Arbitrary Field Read via loadRelatedData Discloses Password Hashes and Salts

## Summary
Severity: Medium
Advisory: CVE-2026-70557
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70557
Type: osv

## Details
diboot-core's POST /common/load-related-data endpoint resolves caller-supplied field names to any @TableField column of any entity and returns those values for all rows, with no field or entity allowlist. The only guard, relatedDataSecurityCheck(), returns true unconditionally, so any authenticated user (including a zero-role account) can read @JsonIgnore-annotated secret fields such as IamAccount.authSecret and IamAccount.secretSalt for every account, or arbitrary secret fields of any other entity. Shiro's two-iteration MD5 with an 8-character salt is trivially crackable offline, so the disclosed admin password hashes convert to full administrative takeover. The endpoint is not example code; the official diboot-admin-ui frontend requires it, so deployments following the vendor's recommended integration expose it. The mechanism was renamed relatedData* to attachMore* on the development branch, but attachMoreSecurityCheck() also returns true unconditionally.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70557.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70557
- https://github.com/dibo-software/diboot
- https://github.com/dibo-software/diboot/issues/104
