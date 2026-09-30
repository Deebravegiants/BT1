# [M] CVE-2024-41258

## Summary
Severity: Medium
Advisory: CVE-2024-41258
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-07-31
Source: https://osv.dev/vulnerability/CVE-2024-41258
Type: osv

## Details
An issue was discovered in filestash v0.4. The usage of the ssh.InsecureIgnoreHostKey() disables host key verification, possibly allowing attackers to obtain sensitive information via a man-in-the-middle attack.

## References
- https://gist.github.com/nyxfqq/ed8c2ba3398c9e28cd8dbf0902bd8edf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41258.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41258
