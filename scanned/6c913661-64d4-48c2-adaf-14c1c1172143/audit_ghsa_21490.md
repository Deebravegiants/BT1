# [H] Payara, when deployed to the root context, allows attackers to visit META-INF and WEB-INF

## Summary
Severity: High
Advisory: GHSA-q35w-85pq-rv3x
CVE: CVE-2022-45129
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-q35w-85pq-rv3x
Type: github-advisory

## Affected
- Maven: `fish.payara.distributions:payara` — affected >=6.2021.1.Alpha1 <6.2022.2
- Maven: `fish.payara.distributions:payara` — affected >=5.0.0.Alpha1 <5.2022.5
- Maven: `fish.payara.distributions:payara` — affected >=0

## Details
Payara before 2022-11-04, when deployed to the root context, allows attackers to visit META-INF and WEB-INF, a different vulnerability than CVE-2022-37422. This affects Payara Platform Community before 4.1.2.191.38, 5.x before 5.2022.4, and 6.x before 6.2022.1, and Payara Platform Enterprise before 5.45.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45129
- https://github.com/payara/Payara/issues/6136
- https://github.com/payara/Payara/commit/cccdfddeda71c78ae7b3179db5429e1bb8a56b2e
- https://blog.payara.fish/whats-new-in-the-november-2022-payara-platform-release
- https://docs.payara.fish/community/docs/6.2022.1/Release%20Notes/Release%20Notes%206.2022.1.html
- https://docs.payara.fish/community/docs/Release%20Notes/Release%20Notes%205.2022.4.html
- https://docs.payara.fish/enterprise/docs/Release%20Notes/Release%20Notes%205.45.0.html
- https://github.com/payara/Payara
- https://github.com/payara/Payara/issues?q=FISH-6775
- http://packetstormsecurity.com/files/169864/Payara-Platform-Path-Traversal.html
- http://seclists.org/fulldisclosure/2022/Nov/11
