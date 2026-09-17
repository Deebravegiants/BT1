# [M] Apache James server allows an attacker with local access to access private user data in transit

## Summary
Severity: Medium
Advisory: GHSA-v6vp-62vc-84qw
CVE: CVE-2022-45935
CWE: CWE-200, CWE-319, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-v6vp-62vc-84qw
Type: github-advisory

## Affected
- Maven: `org.apache.james:james-server` — affected >=0

## Details
Usage of temporary files with insecure permissions by the Apache James server allows an attacker with local access to access private user data in transit. Vulnerable components includes the SMTP stack and IMAP APPEND command. This issue affects Apache James server version 3.7.2 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45935
- https://github.com/apache/james-project/commit/b5580d13d6c74ecbf647127eff1a3ac1086f5493
- https://github.com/apache/james-project
- https://lists.apache.org/thread/j61fo8xc1rxtofrn8vc33whx35s9cj1d
