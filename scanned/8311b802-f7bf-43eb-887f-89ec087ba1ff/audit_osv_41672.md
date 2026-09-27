# [M] Dendrite 0.13.8 Improper Authorization via POST account/3pid/delete Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-63095
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-63095
Type: osv

## Details
Dendrite through 0.13.8 contains an improper authorization vulnerability in the Matrix Client-Server API that allows any authenticated local user to delete third-party identifier bindings belonging to other users by submitting an arbitrary address and medium to the account deletion endpoint without ownership verification. Attackers can exploit the unverified Forget3PID handler to remove a victim's email or MSISDN binding and subsequently rebind the address through an identity server to hijack the victim's password reset flow.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63095.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63095
- https://www.vulncheck.com/advisories/dendrite-improper-authorization-via-post-account-3pid-delete-endpoint
- https://github.com/matrix-org/dendrite
- https://github.com/geo-chen/oss/blob/main/dendrite.md#finding-1-idor-in-post-account3piddelete-allows-any-authenticated-user-to-remove-any-other-users-third-party-identifier
