# [M] Cuba has a DoS in the File Storage

## Summary
Severity: Medium
Advisory: GHSA-w3mp-6vrj-875g
CVE: CVE-2025-32959
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-22
Source: https://github.com/advisories/GHSA-w3mp-6vrj-875g
Type: github-advisory

## Affected
- Maven: `com.haulmont.cuba:cuba-core` — affected >=0 <7.2.23

## Details
### Impact

The local file storage implementation does not restrict the size of uploaded files. An attacker could exploit this by uploading excessively large files, potentially causing the server to run out of space and return HTTP 500 error, resulting in a denial of service.

The severity of the vulnerability is mitigated by the fact that the application UI and the generic REST API are typically accessible only to authenticated users.

### Patches

The problem has been fixed in CUBA 7.2.23.

### Workarounds

A workaround for those who are unable to upgrade: [Disable Files Endpoint in CUBA Application](https://docs.jmix.io/jmix/files-vulnerabilities.html#disable-files-endpoint-in-cuba-application).

### References

[Files Functionality Vulnerabilities :: Jmix Documentation](https://docs.jmix.io/jmix/files-vulnerabilities.html)

Similar vulnerability in Jmix: [DoS in the Local File Storage · Advisory · jmix-framework/jmix](https://github.com/jmix-framework/jmix/security/advisories/GHSA-f3gv-cwwh-758m)

## References
- https://github.com/cuba-platform/cuba/security/advisories/GHSA-w3mp-6vrj-875g
- https://github.com/jmix-framework/jmix/security/advisories/GHSA-f3gv-cwwh-758m
- https://nvd.nist.gov/vuln/detail/CVE-2025-32959
- https://github.com/cuba-platform/cuba/commit/42b6c00fd0572b8e52ae31afd1babc827a3161a1
- https://docs.jmix.io/jmix/files-vulnerabilities.html
- https://docs.jmix.io/jmix/files-vulnerabilities.html#disable-files-endpoint-in-cuba-application
- https://github.com/cuba-platform/cuba
