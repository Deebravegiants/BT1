# [H] CVE-2024-24431

## Summary
Severity: High
Advisory: CVE-2024-24431
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-24431
Type: osv

## Details
A reachable assertion in the ogs_nas_emm_decode function of Open5GS v2.7.0 allows attackers to cause a Denial of Service (DoS) via a crafted NAS packet with a zero-length EMM message length.

## References
- https://cellularsecurity.org/ransacked
- https://open5gs.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24431.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24431
