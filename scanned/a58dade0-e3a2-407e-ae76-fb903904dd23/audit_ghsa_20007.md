# [M] DSInternals Credential Roaming Elevation of Privilege Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vx2x-9cff-fhjw
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-12-06
Source: https://github.com/advisories/GHSA-vx2x-9cff-fhjw
Type: github-advisory

## Affected
- NuGet: `DSInternals.Common` — affected >=2.21 <4.8

## Details
### Impact

A vulnerability exists in the `DSInternals.Common.Data.RoamedCredential.Save()` method, which incorrectly parses the `msPKIAccountCredentials` LDAP attribute values. As a consequence, a malicious actor would be able to modify the file system of the computer where an application using this function is executed with administrative privileges.

A [similar security issue](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-30170) used to be present in the Windows operating system, as DSInternals re-implements the Credential Roaming feature of Windows.

### Exploitability

The vulnerability can be exploited under the following circumstances:
- An attacker is able to modify the `msPKIAccountCredentials` attribute of a user account in Active Directory. This attribute is used by the Credential Roaming feature of Windows and each AD user can modify their own roamed credentials. AND
- A 3rd party application uses the `DSInternals.Common` library to export roamed credentials from Active Directory to a file system. AND
- The application has administrative privileges on the local system.

The probability of any 3rd-party product using the `DSInternals.Common` library being affected by this vulnerability is extremely low.

### Patches

The issue had been fixed in DSInternals 4.8.

### References

https://www.mandiant.com/resources/blog/apt29-windows-credential-roaming

## References
- https://github.com/MichaelGrafnetter/DSInternals/security/advisories/GHSA-vx2x-9cff-fhjw
- https://nvd.nist.gov/vuln/detail/CVE-2022-30170
- https://github.com/MichaelGrafnetter/DSInternals
- https://www.mandiant.com/resources/blog/apt29-windows-credential-roaming
