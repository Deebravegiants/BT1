# [M] CVE-2024-36078

## Summary
Severity: Medium
Advisory: CVE-2024-36078
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-36078
Type: osv

## Details
In Zammad before 6.3.1, a Ruby gem bundled by Zammad is installed with world-writable file permissions. This allowed a local attacker on the server to modify the gem's files, injecting arbitrary code into Zammad processes (which run with the environment and permissions of the Zammad user).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36078.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36078
- https://zammad.com/en/advisories/zaa-2024-04
