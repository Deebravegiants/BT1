# [H] AutoGPT: SSRF-to-RCE Chain in `SendWebRequestBlock` via IP validation bypass and internal `pg-meta` access

## Summary
Severity: High
Advisory: CVE-2026-56663
Aliases: GHSA-8qc5-rhmg-r6r6
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-56663
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Prior to 0.6.52, an authenticated user can bypass the SSRF / private-IP protections in SendWebRequestBlock and reach internal network services. _is_ip_blocked() in backend/backend/util/request.py does not normalize IPv4-mapped IPv6 addresses before checking resolved IPs against the blocked IPv4 ranges, and does not block special-use ranges such as 100.64.0.0/10 (CGNAT, RFC 6598). A hostname that resolves to an IPv4-mapped IPv6 address therefore passes validation and the request reaches the embedded internal IPv4 endpoint. This affects all AutoGPT Platform deployments. This vulnerability is fixed in 0.6.52.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56663.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-8qc5-rhmg-r6r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-56663
