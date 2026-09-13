# [H] free5GC UDM DataChangeNotification Procedure Panic Due to Nil Pointer Dereference

## Summary
Severity: High
Advisory: GHSA-7g27-v5wj-jr75
CVE: CVE-2026-33064
CWE: CWE-476, CWE-478
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-7g27-v5wj-jr75
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udm` — affected >=0 <1.4.2

## Details
**Impact**  
This is a NULL Pointer Dereference vulnerability leading to Denial of Service.  
- **Security Impact**: A remote attacker can cause the UDM service to panic and crash by sending a crafted POST request to the `/sdm-subscriptions` endpoint with a malformed URL path containing path traversal sequences (`../`) and a large JSON payload. The `DataChangeNotificationProcedure` function in `notifier.go` attempts to access a nil pointer without proper validation, causing a complete service crash with "runtime error: invalid memory address or nil pointer dereference".  
- **Functional Impact**: The service crashes completely, requiring manual restart. All UDM functionality is disrupted until recovery.  
- **Affected Parties**: All deployments of free5GC v4.0.1 using the UDM HTTP callback functionality.

**Patches**  
Yes, the issue has been patched.  
The fix is implemented in PR free5gc/udm#78.  
Users should upgrade to the next release of free5GC that includes this commit.

**Workarounds**  
There is no direct workaround at the application level. The recommendation is to apply the provided patch or implement API gateway-level filtering to block requests containing path traversal sequences.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-7g27-v5wj-jr75
- https://nvd.nist.gov/vuln/detail/CVE-2026-33064
- https://github.com/free5gc/free5gc/issues/781
- https://github.com/free5gc/udm/pull/78
- https://github.com/free5gc/udm/commit/65d7070f4bfd016864cbbaefbd506bbc85d2fa92
- https://github.com/free5gc/udm
