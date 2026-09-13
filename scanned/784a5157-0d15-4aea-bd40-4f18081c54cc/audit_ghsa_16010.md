# [M] Gradio performs a non-constant-time comparison when comparing hashes

## Summary
Severity: Medium
Advisory: GHSA-j757-pf57-f8r4
CVE: CVE-2024-47869
CWE: CWE-203, CWE-208
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-j757-pf57-f8r4
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.44.0

## Details
### Impact  
**What kind of vulnerability is it? Who is impacted?**

This vulnerability involves a **timing attack** in the way Gradio compares hashes for the `analytics_dashboard` function. Since the comparison is not done in constant time, an attacker could exploit this by measuring the response time of different requests to infer the correct hash byte-by-byte. This can lead to unauthorized access to the analytics dashboard, especially if the attacker can repeatedly query the system with different keys.

### Patches  
Yes, please upgrade to `gradio>4.44` to mitigate this issue.

### Workarounds  
**Is there a way for users to fix or remediate the vulnerability without upgrading?**

To mitigate the risk before applying the patch, developers can manually patch the `analytics_dashboard` dashboard to use a **constant-time comparison** function for comparing sensitive values, such as hashes. Alternatively, access to the analytics dashboard can be disabled.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-j757-pf57-f8r4
- https://nvd.nist.gov/vuln/detail/CVE-2024-47869
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-199.yaml
