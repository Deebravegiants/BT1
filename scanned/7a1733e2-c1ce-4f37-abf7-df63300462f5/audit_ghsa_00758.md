# [C] Authentication Bypass For Endpoints With Anonymous Access in Opencast

## Summary
Severity: Critical
Advisory: GHSA-vmm6-w4cf-7f3x
CVE: CVE-2020-5206
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-01-30
Source: https://github.com/advisories/GHSA-vmm6-w4cf-7f3x
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-kernel` — affected >=0 <7.6
- Maven: `org.opencastproject:opencast-kernel` — affected >=8.0 <8.1

## Details
### Impact

Using a remember-me cookie with an arbitrary username can cause Opencast to assume proper authentication for that user even if the remember-me cookie was incorrect given that the attacked endpoint also allows anonymous access.

This way, an attacker can, for example, fake a remember-me token, assume the identity of the global system administrator and request non-public content from the search service without ever providing any proper authentication.


### Patches

This problem is fixed in Opencast 7.6 and Opencast 8.1


### Workarounds

As a workaround for older, unpatched versions, disabling remember-me cookies in `etc/security/mh_default_org.xml` will mitigate the problem but will obviously also disable this feature without obvious indication. To deactivate this, remove the following line from the security configuration:

```xml
<sec:remember-me … />
```

### References

- [Remember-me cookie in the security configuration file](https://github.com/opencast/opencast/blob/161ee619382f144dc35eea211fc6b556025b98e1/etc/security/mh_default_org.xml#L335-L336)


### For more information

If you have any questions or comments about this advisory:

- Open an issue in [opencast/opencast](https://github.com/opencast/opencast/issues)
- For security-relevant information, email us at security@opencast.org

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-vmm6-w4cf-7f3x
- https://nvd.nist.gov/vuln/detail/CVE-2020-5206
- https://github.com/opencast/opencast/commit/b157e1fb3b35991ca7bf59f0730329fbe7ce82e8
