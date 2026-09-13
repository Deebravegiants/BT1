# [H] Origin Validation Error in Apache NiFi 

## Summary
Severity: High
Advisory: GHSA-jvx9-rj3w-jq99
CVE: CVE-2017-7667
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jvx9-rj3w-jq99
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=0 <0.7.4
- Maven: `org.apache.nifi:nifi` — affected >=1.0.0 <1.3.0

## Details
Apache NiFi before 0.7.4 and 1.x before 1.3.0 need to establish the response header telling browsers to only allow framing with the same origin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7667
- https://lists.apache.org/thread.html/d779d6129de1a5aa149c219b2fc6e9e78156614eaac92a89cbaf9bce@%3Cdev.nifi.apache.org%3E
- http://www.securityfocus.com/bid/99018
