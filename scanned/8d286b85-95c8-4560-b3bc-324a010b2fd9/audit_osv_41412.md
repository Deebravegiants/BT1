# [M] Zeek < 8.0.9 Null Pointer Dereference DoS via Kerberos KRB_ERROR Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-60109
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-60109
Type: osv

## Details
Zeek before 8.0.9 contains a null pointer dereference vulnerability in its Kerberos protocol analyzer that allows unauthenticated remote attackers to crash the sensor by sending a crafted KRB_ERROR message with error-code 25 (KDC_ERR_PREAUTH_REQUIRED) containing a PA-DATA element with padata-type 2, 3, 11, or 19. Attackers can exploit a parser and analyzer state mismatch where proc_padata() dereferences an uninitialized pa_data_element field selected by the wrong parsing arm, triggering a crash via a single UDP or TCP packet to port 88 without any credentials or prior authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60109.json
- https://github.com/zeek/zeek/releases/tag/v8.0.9
- https://nvd.nist.gov/vuln/detail/CVE-2026-60109
- https://www.vulncheck.com/advisories/zeek-null-pointer-dereference-dos-via-kerberos-krb-error-parsing
- https://github.com/zeek/zeek/commit/c82e3c734893d932e94310aec0dbeb1ffcea169d
- https://github.com/zeek/zeek
