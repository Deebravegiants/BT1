# [H] Sipp/sipp: sipp: denial of service and potential arbitrary code execution vulnerability

## Summary
Severity: High
Advisory: CVE-2026-0710
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-0710
Type: osv

## Details
A flaw was found in SIPp. A remote attacker could exploit this by sending specially crafted Session Initiation Protocol (SIP) messages during an active call. This vulnerability, a NULL pointer dereference, can cause the application to crash, leading to a denial of service. Under specific conditions, it may also allow an attacker to execute unauthorized code, compromising the system's integrity and availability.

## References
- https://access.redhat.com/security/cve/CVE-2026-0710
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0710.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0710
- https://bugzilla.redhat.com/show_bug.cgi?id=2427788
- https://github.com/SIPp/sipp
