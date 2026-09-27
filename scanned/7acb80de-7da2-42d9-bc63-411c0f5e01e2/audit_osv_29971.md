# [H] CVE-2024-48080

## Summary
Severity: High
Advisory: CVE-2024-48080
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-03
Source: https://osv.dev/vulnerability/CVE-2024-48080
Type: osv

## Details
An issue in aedes v0.51.2 allows attackers to cause a Denial of Service(DoS) via a crafted request. NOTE: the Supplier indicates that exploitation cannot occur because of the protection mechanism in the validateTopic function in lib/utils.js.

## References
- https://gist.github.com/mcollina/f06af2098665e4bb8372104425f3999e
- https://gist.github.com/pengwGit/cd3c1701a9e05b424fa6c60d86845de4
- https://github.com/moscajs/aedes/releases/tag/v0.51.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48080.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48080
- https://github.com/moscajs/aedes/issues/1024
- https://github.com/moscajs/aedes/issues/1024#issuecomment-2671695219
