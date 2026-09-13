# [M] Allocation of Resources Without Limits or Throttling in Spring Framework

## Summary
Severity: Medium
Advisory: GHSA-rqph-vqwm-22vc
CVE: CVE-2022-22971
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rqph-vqwm-22vc
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-messaging` — affected >=5.3.0 <5.3.20
- Maven: `org.springframework:spring-messaging` — affected >=0 <5.2.22.RELEASE

## Details
In spring framework versions prior to 5.3.20+ , 5.2.22+ and old unsupported versions, application with a STOMP over WebSocket endpoint is vulnerable to a denial of service attack by an authenticated user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22971
- https://github.com/spring-projects/spring-framework/commit/159a99bbafdd6c01871228113d7042c3f83f360f
- https://github.com/spring-projects/spring-framework/commit/dc2947c52df18d5e99cad03383f7d6ba13d031fd
- https://github.com/spring-projects/spring-framework
- https://security.netapp.com/advisory/ntap-20220616-0003
- https://tanzu.vmware.com/security/cve-2022-22971
- https://www.oracle.com/security-alerts/cpujul2022.html
