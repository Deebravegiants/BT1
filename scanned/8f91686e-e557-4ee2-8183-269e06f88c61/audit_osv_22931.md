# [H] CVE-2022-41318

## Summary
Severity: High
Advisory: CVE-2022-41318
Aliases: GHSA-394c-rr7q-6g78
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/CVE-2022-41318
Type: osv

## Details
A buffer over-read was discovered in libntlmauth in Squid 2.5 through 5.6. Due to incorrect integer-overflow protection, the SSPI and SMB authentication helpers are vulnerable to reading unintended memory locations. In some configurations, cleartext credentials from these locations are sent to a client. This is fixed in 5.7.

## References
- http://www.squid-cache.org/Versions/v4/changesets/SQUID-2022_2.patch
- http://www.squid-cache.org/Versions/v5/changesets/SQUID-2022_2.patch
- https://www.openwall.com/lists/oss-security/2022/09/23/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41318.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-394c-rr7q-6g78
- https://nvd.nist.gov/vuln/detail/CVE-2022-41318
