# [C] Webmin HTTP header authentication bypass

## Summary
Severity: Critical
Advisory: CVE-2026-56020
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-56020
Type: osv

## Details
The Webmin HTTP server (miniserv.pl) allows unauthenticated attackers to impersonate any user with a configured SSL client certificate by sending a forged HTTP header. A remote attacker can spoof certificate DNs and authenticate as any user. Fixed in 2.202.

## References
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2026/va-26-169-02.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56020.json
- https://github.com/webmin/webmin/releases/tag/2.202
- https://nvd.nist.gov/vuln/detail/CVE-2026-56020
- https://webmin.com/security/#webmin-prior-to-2202
- https://www.cve.org/CVERecord?id=CVE-2026-56020
