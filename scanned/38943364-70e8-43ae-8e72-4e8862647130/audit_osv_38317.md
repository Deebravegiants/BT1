# [C] CVE-2026-38447

## Summary
Severity: Critical
Advisory: CVE-2026-38447
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-38447
Type: osv

## Details
osTicket 1.18.3 generates API keys using a predictable construction based on MD5 hashing. The use of MD5, combined with predictable inputs such as the current timestamp and client IP address, significantly reduces entropy. An attacker can approximate the key generation time and brute-force the key space within a feasible time window.

## References
- https://github.com/fr3akhacks/cve-disclosures/blob/master/osTicket/CVE-2026-38447.md
- https://github.com/osTicket/osTicket/blob/v1.18.3/include/class.api.php#L149
- https://github.com/osTicket/osTicket/blob/v1.18.3/include/class.misc.php
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38447
- https://github.com/osTicket/osTicket/commit/feccb6a3a90863fd31215ee738b39762177e658c
