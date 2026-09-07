# [M] Users with ROLE_COURSE_ADMIN can create new users in Opencast

## Summary
Severity: Medium
Advisory: GHSA-94qw-r73x-j7hg
CVE: CVE-2020-5231
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-01-30
Source: https://github.com/advisories/GHSA-94qw-r73x-j7hg
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-kernel` — affected >=0 <7.6
- Maven: `org.opencastproject:opencast-kernel` — affected >=8.0 <8.1

## Details
### Impact

Users with the role `ROLE_COURSE_ADMIN` can use the user-utils endpoint to create new users not including the role `ROLE_ADMIN`. For example:

```bash
# Use the admin to create a new user with ROLE_COURSE_ADMIN using the admin user.
# We expect this to work.
% curl -i -u admin:opencast 'https://example.opencast.org/user-utils/xy.json' -X PUT \
  --data 'password=f&roles=%5B%22ROLE_COURSE_ADMIN%22%5D'
HTTP/2 201

# Use the new user to create more new users.
# We don't expüect a user with just role ROLE_COURSE_ADMIN to succeed.
# But it does work
% curl -i -u xy:f 'https://example.opencast.org/user-utils/ab.json' -X PUT \
  --data 'password=f&roles=%5B%22ROLE_COURSE_ADMIN%22%5D'
HTTP/2 201
```
`ROLE_COURSE_ADMIN` is a non-standard role in Opencast which is referenced neither in the documentation nor in any code (except for tests) but only in the security configuration. From the name – implying an admin for a specific course – users would never expect that this role allows user creation.

### Patches

This issue is fixed in 7.6 and 8.1 which both ship a new default security configuration.

### Workarounds

You can fix this issue by removing all instances of `ROLE_COURSE_ADMIN` in your organization's security configuration (`etc/security/mh_default_org.xml` by default).

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [opencast/opencast](https://github.com/opencast/opencast/issues)
- For security-relevant information, email us at security@opencast.org

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-94qw-r73x-j7hg
- https://nvd.nist.gov/vuln/detail/CVE-2020-5231
- https://github.com/opencast/opencast/commit/72fad0031d8a82c860e2bde0b27570c5042320ee
