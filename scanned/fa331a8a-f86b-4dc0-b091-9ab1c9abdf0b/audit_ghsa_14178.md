# [M] org.xwiki.platform:xwiki-platform-security-authentication-default XSS with authenticate endpoints

## Summary
Severity: Medium
Advisory: GHSA-jjm5-5v9v-7hx2
CVE: CVE-2023-29506
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-jjm5-5v9v-7hx2
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-security-authentication-default` — affected >=13.10.8 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-security-authentication-default` — affected >=14.4.3 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-security-authentication-default` — affected >=14.6 <14.10

## Details
### Impact

It was possible to inject some code using the URL of authenticate endpoints, e.g.:

```
https://hostname/xwiki/authenticate/wiki/xwiki%22onload=%22alert(origin)%22/resetpassword
```

This vulnerability was present in recent versions of XWiki:
  - 13.10.8+
  - 14.4.3+
  - 14.6+

### Patches

This problem has been patched on XWiki 13.10.11, 14.4.7 and 14.10.

### Workarounds
There is no easy workaround except to upgrade.

### References

  - https://jira.xwiki.org/browse/XWIKI-20335
  - https://github.com/xwiki/xwiki-platform/commit/1943ea26c967ef868fb5f67c487d98d97cba0380

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](https://jira.xwiki.org)
* Email us at [security mailing-list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-jjm5-5v9v-7hx2
- https://nvd.nist.gov/vuln/detail/CVE-2023-29506
- https://github.com/xwiki/xwiki-platform/commit/1943ea26c967ef868fb5f67c487d98d97cba0380
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20335
