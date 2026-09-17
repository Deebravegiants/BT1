# [M] CVE-2023-37360

## Summary
Severity: Medium
Advisory: CVE-2023-37360
Aliases: GHSA-62q6-v997-f7v9, PYSEC-2023-93
CVSS: 5.9 (CVSS:3.1/AC:L/AV:L/A:L/C:L/I:L/PR:N/S:U/UI:N)
Published: 2023-06-30
Source: https://osv.dev/vulnerability/CVE-2023-37360
Type: osv

## Details
pacparser_find_proxy in Pacparser before 1.4.2 allows JavaScript injection, and possibly privilege escalation, when the attacker controls the URL (which may be realistic within enterprise security products).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37360.json
- https://github.com/manugarg/pacparser/security/advisories/GHSA-62q6-v997-f7v9
- https://nvd.nist.gov/vuln/detail/CVE-2023-37360
