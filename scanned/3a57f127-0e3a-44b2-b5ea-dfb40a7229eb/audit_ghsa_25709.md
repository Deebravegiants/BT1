# [H] Arbitrary filesystem write access from velocity.

## Summary
Severity: High
Advisory: GHSA-cvx5-m8vg-vxgc
CVE: CVE-2022-24897
CWE: CWE-22, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-28
Source: https://github.com/advisories/GHSA-cvx5-m8vg-vxgc
Type: github-advisory

## Affected
- Maven: `org.xwiki.commons:xwiki-commons-velocity` — affected >=2.3.0 <12.6.7
- Maven: `org.xwiki.commons:xwiki-commons-velocity` — affected >=12.7.0 <12.10.3

## Details
### Impact

The velocity scripts is not properly sandboxed against using the Java File API to perform read or write operations on the filesystem. Now writing an attacking script in velocity requires the Script rights in XWiki so not all users can use it, and it also requires finding an XWiki API which returns a File. 

### Patches
The problem has been patched on versions 12.6.7, 12.10.3 and 13.0RC1.

### Workarounds
There's no easy workaround for fixing this vulnerability other than upgrading and being careful when giving Script rights.

### References
https://jira.xwiki.org/browse/XWIKI-5168

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [XWiki Security mailing-list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-commons/security/advisories/GHSA-cvx5-m8vg-vxgc
- https://nvd.nist.gov/vuln/detail/CVE-2022-24897
- https://github.com/xwiki/xwiki-commons/pull/127
- https://github.com/xwiki/xwiki-commons/commit/215951cfb0f808d0bf5b1097c9e7d1e503449ab8
- https://github.com/xwiki/xwiki-commons
- https://jira.xwiki.org/browse/XWIKI-5168
