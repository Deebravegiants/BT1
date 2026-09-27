# [H] Csmock: command injection vulnerability in csmock-plugin-snyk

## Summary
Severity: High
Advisory: CVE-2024-2243
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-2243
Type: osv

## Details
A vulnerability was found in csmock where a regular user of the OSH service (anyone with a valid Kerberos ticket) can use the vulnerability to disclose the confidential Snyk authentication token and to run arbitrary commands on OSH workers.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I5MJC7U2ZKXUZWELQUJSN56WL5IM4MDR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TIBNRL3LTG747DNWTBCPRSNRPKOBANMX/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X3HF6YTEGGW3SWB4V7JUVIRCXIBRHR7A/
- https://access.redhat.com/security/cve/CVE-2024-2243
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2243.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2243
- https://bugzilla.redhat.com/show_bug.cgi?id=2267336
- https://github.com/csutils/csmock
