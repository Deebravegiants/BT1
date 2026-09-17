# [M] Conformance validation endpoint discloses detail about service to unauthenticated users

## Summary
Severity: Medium
Advisory: CVE-2024-9802
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N/E:U/RL:O/RC:C)
Published: 2024-10-10
Source: https://osv.dev/vulnerability/CVE-2024-9802
Type: osv

## Details
The conformance validation endpoint is public so everybody can verify the conformance of onboarded services. The response could contain specific information about the service, including available endpoints, and swagger. It could advise about the running version of a service to an attacker. The attacker could also check if a service is running.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9802.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9802
- https://github.com/zowe/api-layer
