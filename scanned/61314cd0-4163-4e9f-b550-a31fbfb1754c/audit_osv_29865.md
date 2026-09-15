# [H] Suricata datasets: missing hashtable random seed leads to potential DoS

## Summary
Severity: High
Advisory: CVE-2024-47187
Aliases: GHSA-64ww-4f6x-863p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-16
Source: https://osv.dev/vulnerability/CVE-2024-47187
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to version 7.0.7, missing initialization of the random seed for "thash" leads to datasets having predictable hash table behavior. This can lead to dataset file loading to use excessive time to load, as well as runtime performance issues during traffic handling. This issue has been addressed in 7.0.7. As a workaround, avoid loading datasets from untrusted sources. Avoid dataset rules that track traffic in rules.

## References
- https://redmine.openinfosecfoundation.org/issues/7209
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47187.json
- https://github.com/OISF/suricata/security/advisories/GHSA-64ww-4f6x-863p
- https://nvd.nist.gov/vuln/detail/CVE-2024-47187
