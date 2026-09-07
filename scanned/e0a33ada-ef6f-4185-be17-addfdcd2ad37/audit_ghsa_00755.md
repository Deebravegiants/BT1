# [H] Unauthenticated Access Via OAI-PMH

## Summary
Severity: High
Advisory: GHSA-6f54-3qr9-pjgj
CVE: CVE-2020-5228
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2020-01-30
Source: https://github.com/advisories/GHSA-6f54-3qr9-pjgj
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-oaipmh-api` — affected >=0 <7.6
- Maven: `org.opencastproject:opencast-oaipmh-api` — affected >=8.0 <8.1

## Details
### Impact

Media publication via OAI-PMH allows unauthenticated public access to all media and metadata by default. OAI-PMH is part of the default workflow and is activated by default, requiring active user intervention of users to protect media. This leads to users unknowingly handing out public access to events without their knowledge.


### Patches

The problem has been addressed in Opencast 7.6 and 8.1 where the OAI-PMH endpoint is configured to require users with `ROLE_ADMIN` by default. In addition to this, Opencast 9 removes the OAI-PMH publication from the default workflow, making the publication a conscious decision users have to make by updating their workflows.

### Workarounds

In the organization security configuration (`etc/security/mh_default_org.xml`), change the roles required for accessing `/oaipmh` from `ROLE_ANONYMOUS` to `ROLE_ADMIN`.

### References

- [Public access configuration in the organization's security configuration](https://github.com/opencast/opencast/blob/1fb812c7810c78f09f29a7f455ff920417924307/etc/security/mh_default_org.xml#L271-L276)

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [opencast/opencast](https://github.com/opencast/opencast/issues)
- For security-relevant information, email us at security@opencast.org

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-6f54-3qr9-pjgj
- https://nvd.nist.gov/vuln/detail/CVE-2020-5228
- https://github.com/opencast/opencast/blob/1fb812c7810c78f09f29a7f455ff920417924307/etc/security/mh_default_org.xml#L271-L276
