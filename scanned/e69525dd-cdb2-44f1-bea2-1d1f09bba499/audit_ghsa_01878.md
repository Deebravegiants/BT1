# [H] Opencast publishes global system account credentials

## Summary
Severity: High
Advisory: GHSA-hcxx-mp6g-6gr9
CVE: CVE-2018-16153
CWE: CWE-200, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-hcxx-mp6g-6gr9
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-common` — affected >=0 <10.6

## Details
The issue was mostly mitigated before, drastically reducing the risk. See references below for more information.

### Impact

Opencast before version 10.6 will try to authenticate against any external services listed in a media package when it is trying to access the files, sending the global system user's credentials, regardless of the target being part of the Opencast cluster or not.

Previous mitigations already prevented clear text authentications for such requests (e.g. HTTP Basic authentication), but with enough malicious intent, even hashed credentials can be broken.

### Patches

Opencast 10.6 will now send authentication requests only against servers which are part of the Opencast cluster, preventing external services from getting any form of authentication attempt in the first place.

### Workarounds

No workaround available.

### References

- [Patch fixing the issue](https://github.com/opencast/opencast/commit/776d5588f39c61eb04c03bb955416c4f77629d51)
- [Original security notice](https://groups.google.com/a/opencast.org/g/security-notices/c/XRZzRiqp-NE)
- [Original security mitigation](https://github.com/opencast/opencast/commit/fe8c3d3a60dc5869b468957270dbad5f8c30ead6)

### For more information

If you have any questions or comments about this advisory:
- Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
- Email us at [security@opencast.org](mailto:security@opencast.org)

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-hcxx-mp6g-6gr9
- https://nvd.nist.gov/vuln/detail/CVE-2018-16153
- https://github.com/opencast/opencast/commit/776d5588f39c61eb04c03bb955416c4f77629d51
- https://docs.opencast.org/r/10.x/admin/#changelog
- https://docs.opencast.org/r/10.x/admin/#changelog/#opencast-106
- https://github.com/advisories/GHSA-hcxx-mp6g-6gr9
- https://github.com/opencast/opencast
- https://www.apereo.org/projects/opencast/news
