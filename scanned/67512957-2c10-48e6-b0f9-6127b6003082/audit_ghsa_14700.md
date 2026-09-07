# [C] XWiki allows remote code execution through the extension sheet

## Summary
Severity: Critical
Advisory: GHSA-j2pq-22jj-4pm5
CVE: CVE-2024-55662
CWE: CWE-863, CWE-94, CWE-96
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-j2pq-22jj-4pm5
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-repository-server-ui` — affected >=3.3-milestone-1 <15.10.9
- Maven: `org.xwiki.platform:xwiki-platform-repository-server-ui` — affected >=16.0.0-rc-1 <16.3.0

## Details
### Impact
On instances where `Extension Repository Application` is installed, any user can execute any code requiring `programming` rights on the server.
In order to reproduce on an instance, as a normal user without `script` nor `programming` rights, go to your profile and add an object of type `ExtensionCode.ExtensionClass`. Set the description to `{{async}}{{groovy}}println("Hello from Description"){{/groovy}}{{/async}}` and press `Save and View`. If the description displays as `Hello from Description` without any error, then the instance is vulnerable.

### Patches
This vulnerability has been fixed in XWiki 15.10.9 and 16.3.0.

### Workarounds
Since `Extension Repository Application` is not mandatory, it can be safely disabled on instances that do not use it.
It is also possible to manually apply [this patch](https://github.com/xwiki/xwiki-platform/commit/8659f17d500522bf33595e402391592a35a162e8#diff-9b6f9e853f23d76611967737f8c4072ffceaba4c006ca5a5e65b66d988dc084a) to the page `ExtensionCode.ExtensionSheet`, as well as [this patch](https://github.com/xwiki/xwiki-platform/commit/8659f17d500522bf33595e402391592a35a162e8#diff-d571404d94fa27360cfee64f2a11d8c819b397529db275e005606b7356610f82) to the page `ExtensionCode.ExtensionAuthorsDisplayer`.

### References
* https://jira.xwiki.org/browse/XWIKI-21890
* https://github.com/xwiki/xwiki-platform/commit/8659f17d500522bf33595e402391592a35a162e8

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-j2pq-22jj-4pm5
- https://nvd.nist.gov/vuln/detail/CVE-2024-55662
- https://github.com/xwiki/xwiki-platform/commit/8659f17d500522bf33595e402391592a35a162e8
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21890
