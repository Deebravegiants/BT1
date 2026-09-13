# [M] Suricata datasets: ruleset declared settings can lead to resource starvation

## Summary
Severity: Medium
Advisory: CVE-2025-29916
Aliases: GHSA-27g3-pmvp-j9cv
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-10
Source: https://osv.dev/vulnerability/CVE-2025-29916
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Datasets declared in rules have an option to specify the `hashsize` to use. This size setting isn't properly limited, so the hash table allocation can be large. Untrusted rules can lead to large memory allocations, potentially leading to denial of service due to resource starvation. This vulnerability is fixed in 7.0.9.

## References
- https://redmine.openinfosecfoundation.org/issues/7615
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29916.json
- https://github.com/OISF/suricata/security/advisories/GHSA-27g3-pmvp-j9cv
- https://nvd.nist.gov/vuln/detail/CVE-2025-29916
- https://github.com/OISF/suricata/commit/a7713db709b8a0be5fc5e5809ab58e9b14a16e85
