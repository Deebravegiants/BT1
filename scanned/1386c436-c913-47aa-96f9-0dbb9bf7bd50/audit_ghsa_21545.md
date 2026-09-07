# [M] Exposure of Private Personal Information to an Unauthorized Actor in org.xwiki.platform:xwiki-platform-rest-server

## Summary
Severity: Medium
Advisory: GHSA-p88w-fhxw-xvcc
CVE: CVE-2022-41936
CWE: CWE-359
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-p88w-fhxw-xvcc
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=8.1 <13.10.8
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=14.0.0 <14.4.3
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=14.5.0 <14.6

## Details
### Impact
The `modifications` rest endpoint does not filter out entries according to the user's rights. Therefore, information hidden from unauthorized users are exposed though the `modifications` rest endpoint (e.g., comments, page names...). 

### Patches
Users should upgrade to XWiki 14.6+, 14.4.3+,  or13.10.8+. Older versions have not been patched.

### Workarounds
No known workaround.

### References

- Patch: https://github.com/xwiki/xwiki-platform/commit/38dc1aa1a4435f24d58f5b8e4566cbcb0971f8ff
- Jira issue: https://jira.xwiki.org/browse/XWIKI-19997

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
- Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-p88w-fhxw-xvcc
- https://nvd.nist.gov/vuln/detail/CVE-2022-41936
- https://github.com/xwiki/xwiki-platform/commit/38dc1aa1a4435f24d58f5b8e4566cbcb0971f8ff
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19997
