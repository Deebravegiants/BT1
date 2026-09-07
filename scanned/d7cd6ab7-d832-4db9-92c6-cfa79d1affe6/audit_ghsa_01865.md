# [H] HTTP Method Spoofing

## Summary
Severity: High
Advisory: GHSA-j4mm-7pj3-jf7v
CVE: CVE-2021-43807
CWE: CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-j4mm-7pj3-jf7v
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-common` — affected >=0 <9.10

## Details
Opencast versions prior to 9.10 allow HTTP method spoofing, allowing to change the assumed HTTP method via URL parameter. This allows  attackers to turn HTTP GET requests into PUT requests or an HTTP form to send DELETE requests. This bypasses restrictions otherwise put on these types of requests and aids in cross-site request forgery (CSRF) attacks, which would otherwise not be possible.

### Impact

The vulnerability allows attackers to craft links or forms which may change the server state. For example, the following GET request would create a new user:

```sh
% curl -i -u admin:opencast \
  'https://legacy.opencast.org/admin-ng/users/test.json?_method=PUT&username=test&password=attack'
HTTP/2 200
…
```

If an admin is logged in to legacy.opencast.org and accidentally clicks this link, a user will silently be created.


### Patches

This issue is fixed in Opencast 9.10 and 10.0.

### Workarounds

You can mitigate the problem by setting the `SameSite=Strict` attribute for your cookies. If this is a viable option for you depends on your integrations. We strongly recommend updating in any case.

### References

- [Fix for 10.0](https://github.com/opencast/opencast/commit/59cb6731067283e54f15462be38b6117d8b9ea8b#diff-9c5fb3d1b7e3b0f54bc5c4182965c4fe1f9023d449017cece3005d3f90e8e4d8)
- [Fix for 9.10](https://github.com/opencast/opencast/commit/8f8271e1085f6f8e306c689d6a56b0bb8d076444)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
* Email us at [security@opencast.org](mailto:security@opencast.org)

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-j4mm-7pj3-jf7v
- https://nvd.nist.gov/vuln/detail/CVE-2021-43807
- https://github.com/opencast/opencast/commit/59cb6731067283e54f15462be38b6117d8b9ea8b#diff-9c5fb3d1b7e3b0f54bc5c4182965c4fe1f9023d449017cece3005d3f90e8e4d8
- https://github.com/opencast/opencast/commit/8f8271e1085f6f8e306c689d6a56b0bb8d076444
- https://github.com/opencast/opencast
