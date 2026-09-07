# [H] Privilege escalation in XXL-Job

## Summary
Severity: High
Advisory: GHSA-9mmj-64jh-ph9c
CVE: CVE-2023-33779
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-9mmj-64jh-ph9c
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job` — affected >=0

## Details
A lateral privilege escalation vulnerability in XXL-Job v2.4.1 allows users to execute arbitrary commands on another user's account via a crafted POST request to the component `/jobinfo/`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33779
- https://github.com/silence-silence/xxl-job-lateral-privilege-escalation-vulnerability-/blob/main/README.md
- https://github.com/xuxueli/xxl-job
- http://xxl-job.com
