# [H] CVE-2023-45839

## Summary
Severity: High
Advisory: CVE-2023-45839
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-05
Source: https://osv.dev/vulnerability/CVE-2023-45839
Type: osv

## Details
Multiple data integrity vulnerabilities exist in the package hash checking functionality of Buildroot 2023.08.1 and Buildroot dev commit 622698d7847. A specially crafted man-in-the-middle attack can lead to arbitrary command execution in the builder.This vulnerability is related to the `aufs-util` package.

## References
- http://www.openwall.com/lists/oss-security/2023/12/11/1
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1844
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1844
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45839.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-45839
