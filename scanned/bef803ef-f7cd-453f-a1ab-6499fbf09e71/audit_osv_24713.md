# [M] Login fail open on JAAS misconfiguration in DataHub

## Summary
Severity: Medium
Advisory: CVE-2023-25561
Aliases: GHSA-7wc6-p6c4-522c
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-02-10
Source: https://osv.dev/vulnerability/CVE-2023-25561
Type: osv

## Details
DataHub is an open-source metadata platform. In the event a system is using Java Authentication and Authorization Service (JAAS) authentication and that system is given a configuration which contains an error, the authentication for the system will fail open and allow an attacker to login using any username and password. The reason for this is that while an error is thrown in the `authenticateJaasUser` method it is swallowed without propagating the error. As a result of this issue unauthenticated users may gain access to the system. Users are advised to upgrade. There are no known workarounds for this issue. This vulnerability was discovered and reported by the GitHub Security lab and is tracked as GHSL-2022-081.

## References
- https://github.com/datahub-project/datahub/blob/fdf4e48495f083314f59c414bcc7c2601633a2b8/datahub-frontend/app/security/AuthenticationManager.java#L26
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25561.json
- https://github.com/datahub-project/datahub/security/advisories/GHSA-7wc6-p6c4-522c
- https://nvd.nist.gov/vuln/detail/CVE-2023-25561
