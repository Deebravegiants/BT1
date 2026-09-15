# [M] Hard-Coded Key Used For Remember-me Token in Opencast

## Summary
Severity: Medium
Advisory: GHSA-mh8g-hprg-8363
CVE: CVE-2020-5222
CWE: CWE-798
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-01-30
Source: https://github.com/advisories/GHSA-mh8g-hprg-8363
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-kernel` — affected >=0 <7.6
- Maven: `org.opencastproject:opencast-kernel` — affected >=8.0 <8.1

## Details
### Impact

The security configuration in `etc/security/mh_default_org.xml` enables a remember-me cookie based on a hash created from the [username, password, and an additional system key](https://docs.spring.io/spring-security/site/docs/3.0.x/reference/remember-me.html). Opencast has hard-coded this system key in the large XML file and never mentions to change this, basically ensuring that all systems use the same key:

```xml
<sec:remember-me key="opencast" user-service-ref="userDetailsService" />
```

This means that an attacker getting access to a remember-me token for one server can get access to all servers which allow log-in using the same credentials without ever needing the credentials. For example, a remember-me token obtained from develop.opencast.org can be used on stable.opencast.org without actually knowing the log-in credentials.

Such an attack will usually not work on different installations – assuming that safe, unique passwords are used – but it is basically guaranteed to work to get access to all machines of one cluster if a token from one machine is compromised.

### Patches

This problem is fixed in Opencast 7.6 and Opencast 8.1

### Workarounds

We strongly recommend updating to the patched version. Still, as a workaround for older versions, in `etc/security/mh_default_org.xml`, set a custom key for each server:

```xml
<sec:remember-me key="CUSTOM_RANDOM_KEY" user-service-ref="userDetailsService" />
```

### References

- [Relevant lines in the security configuration](https://github.com/opencast/opencast/blob/161ee619382f144dc35eea211fc6b556025b98e1/etc/security/mh_default_org.xml#L335-L336)
- [Spring Security Remember-Me Authentication Documentation](https://docs.spring.io/spring-security/site/docs/3.0.x/reference/remember-me.html#remember-me-hash-token)

### For more information
If you have any questions or comments about this advisory:
- Open an issue in [opencast/opencast](https://github.com/opencast/opencast/issues)
- For security-relevant information, email us at [security@opencast.org](mailto:security@opencast.org)

### Thanks
Thanks to @LukasKalbertodt for reporting the issue.

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-mh8g-hprg-8363
- https://nvd.nist.gov/vuln/detail/CVE-2020-5222
- https://github.com/opencast/opencast/commit/1a7172c95af8d542a77ae5b153e4c834dd4788a6
