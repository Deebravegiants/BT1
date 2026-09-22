# [H] Workbench Affected by Remote Code Execution (RCE) via Malicious Cookie in Timezone Conversion

## Summary
Severity: High
Advisory: CVE-2026-35178
Aliases: GHSA-jw63-m86r-2jxc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35178
Type: osv

## Details
Workbench is a suite of tools for administrators and developers to interact with Salesforce.com organizations via the Force.com APIs. Prior to 65.0.0, Workbench contains remote code execution vulnerability in the timezone conversion flow, which processes attacker-controlled cookie values in an unsafe manner. This vulnerability is fixed in 65.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35178.json
- https://github.com/forceworkbench/forceworkbench/security/advisories/GHSA-jw63-m86r-2jxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-35178
- https://github.com/forceworkbench/forceworkbench/pull/869
