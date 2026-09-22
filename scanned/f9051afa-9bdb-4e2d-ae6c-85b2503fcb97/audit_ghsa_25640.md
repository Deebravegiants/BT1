# [H] Hadoop symlink vulnerability

## Summary
Severity: High
Advisory: GHSA-v5c9-98f7-2h54
CVE: CVE-2012-2945
CWE: CWE-377, CWE-59
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-v5c9-98f7-2h54
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-main` — affected >=0 <1.0.4

## Details
Hadoop 1.0.3 contains a symlink vulnerability as a result of storing pid files in the shared `/tmp` directory by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2945
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=535861
- https://github.com/apache/hadoop
- https://seclists.org/fulldisclosure/2012/Jul/3
- https://security-tracker.debian.org/tracker/CVE-2012-2945
