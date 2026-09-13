# [H] Unzip function in ZipUtil.java in Hutool allows remote attackers to overwrite arbitrary files via directory traversal

## Summary
Severity: High
Advisory: GHSA-rhq2-2574-78mc
CVE: CVE-2018-17297
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-rhq2-2574-78mc
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-parent` — affected >=0 <4.1.12
- Maven: `cn.hutool:hutool-all` — affected >=0 <4.1.12
- Maven: `cn.hutool:hutool-core` — affected >=0 <4.1.12

## Details
The unzip function in ZipUtil.java in Hutool before 4.1.12 allows remote attackers to overwrite arbitrary files via directory traversal sequences in a filename within a ZIP archive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17297
- https://github.com/looly/hutool/issues/162
- https://github.com/advisories/GHSA-rhq2-2574-78mc
- https://github.com/looly/hutool
