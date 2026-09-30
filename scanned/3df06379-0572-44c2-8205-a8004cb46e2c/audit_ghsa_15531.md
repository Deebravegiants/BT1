# [M] Eclipse Glassfish improperly handles http parameters

## Summary
Severity: Medium
Advisory: GHSA-jq3f-mfmg-747x
CVE: CVE-2024-9329
CWE: CWE-233, CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-30
Source: https://github.com/advisories/GHSA-jq3f-mfmg-747x
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.admin:rest-service` — affected >=0 <7.0.17

## Details
In Eclipse Glassfish versions before 7.0.17, the Host HTTP parameter could cause the web application to redirect to the specified URL, when the requested endpoint is `/management/domain`. By modifying the URL value to a malicious site, an attacker may successfully launch a phishing scam and steal user credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9329
- https://github.com/eclipse-ee4j/glassfish/pull/25106
- https://github.com/eclipse-ee4j/glassfish/commit/6ca35eee2ba90a8108984b27bec33f9cc50cd83b
- https://github.com/eclipse-ee4j/glassfish
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/232
