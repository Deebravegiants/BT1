# [C] CVE-2024-33668

## Summary
Severity: Critical
Advisory: CVE-2024-33668
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-26
Source: https://osv.dev/vulnerability/CVE-2024-33668
Type: osv

## Details
An issue was discovered in Zammad before 6.3.0. The Zammad Upload Cache uses insecure, partially guessable FormIDs to identify content. An attacker could try to brute force them to upload malicious content to article drafts they have no access to.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33668.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33668
- https://zammad.com/en/advisories/zaa-2024-02
