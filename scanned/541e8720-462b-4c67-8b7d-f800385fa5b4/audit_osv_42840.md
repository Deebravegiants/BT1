# [M] OP-TEE OS 4.10.0 NULL Pointer Dereference DoS via Widevine PTA open_session

## Summary
Severity: Medium
Advisory: CVE-2026-71967
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-71967
Type: osv

## Details
OP-TEE OS through 4.10.0, fixed in commit 0aadfc2, contains a null pointer dereference vulnerability in the Widevine pseudo-TA open_session handler that allows Normal World clients to cause a denial of service when CFG_WIDEVINE_PTA is enabled. Attackers can open a session directly on the Widevine PTA to trigger an unconditional dereference of a NULL calling session pointer via is_user_ta_ctx(), faulting the TEE at S-EL1 and crashing the trusted execution environment.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71967.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71967
- https://www.vulncheck.com/advisories/op-tee-os-null-pointer-dereference-dos-via-widevine-pta-open-session
- https://github.com/OP-TEE/optee_os/pull/7899
- https://github.com/OP-TEE/optee_os/commit/0aadfc23407f50e770eb5ddd871fc208f5626833
- https://github.com/OP-TEE/optee_os
