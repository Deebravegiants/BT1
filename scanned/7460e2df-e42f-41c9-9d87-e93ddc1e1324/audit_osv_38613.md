# [C] CVE-2026-40982

## Summary
Severity: Critical
Advisory: CVE-2026-40982
Aliases: GHSA-6g23-24mc-hx6x
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-40982
Type: osv

## Details
Spring Cloud Config allows applications to serve arbitrary text and binary files through the spring-cloud-config-server module. A malicious user, or attacker, can send a request using a specially crafted URL that can lead to a directory traversal attack.
Spring Cloud Config 3.1.x: affected from 3.1.0 through 3.1.13 (inclusive); upgrade to 3.1.14 or greater (Enterprise Support Only). Spring Cloud Config 4.1.x: affected from 4.1.0 through 4.1.9 (inclusive); upgrade to 4.1.10 or greater (Enterprise Support Only). Spring Cloud Config 4.2.x: affected from 4.2.0 through 4.2.6 (inclusive); upgrade to 4.2.7 or greater (Enterprise Support Only). Spring Cloud Config 4.3.x: affected from 4.3.0 through 4.3.2 (inclusive); upgrade to 4.3.3 or greater. Spring Cloud Config 5.0.x: affected from 5.0.0 through 5.0.2 (inclusive); upgrade to 5.0.3 or greater.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40982.json
- https://spring.io/security/cve-2026-40982
- https://access.redhat.com/security/cve/CVE-2026-40982
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40982.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40982
- https://bugzilla.redhat.com/show_bug.cgi?id=2467619
