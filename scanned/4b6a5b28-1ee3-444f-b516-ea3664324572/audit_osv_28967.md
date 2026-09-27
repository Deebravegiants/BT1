# [H] Suricata http/range: NULL-ptr deref when http.memcap is reached

## Summary
Severity: High
Advisory: CVE-2024-38536
Aliases: GHSA-j32j-4w6g-94hh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-11
Source: https://osv.dev/vulnerability/CVE-2024-38536
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. A memory allocation failure due to `http.memcap` being reached leads to a NULL-ptr reference leading to a crash. Upgrade to 7.0.6.

## References
- https://redmine.openinfosecfoundation.org/issues/7029
- https://redmine.openinfosecfoundation.org/issues/7033
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38536.json
- https://github.com/OISF/suricata/security/advisories/GHSA-j32j-4w6g-94hh
- https://nvd.nist.gov/vuln/detail/CVE-2024-38536
