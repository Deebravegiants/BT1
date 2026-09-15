# [H] Suricata krb5: quadratic complexity in krb5 buffering

## Summary
Severity: High
Advisory: CVE-2026-31932
Aliases: GHSA-rp9m-jcpw-hggr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-31932
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. Prior to versions 7.0.15 and 8.0.4, inefficiency in KRB5 buffering can lead to performance degradation. This issue has been patched in versions 7.0.15 and 8.0.4.

## References
- https://redmine.openinfosecfoundation.org/issues/8305
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31932.json
- https://github.com/OISF/suricata/security/advisories/GHSA-rp9m-jcpw-hggr
- https://nvd.nist.gov/vuln/detail/CVE-2026-31932
