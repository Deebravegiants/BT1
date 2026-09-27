# [H] Element Android Intent Redirection

## Summary
Severity: High
Advisory: CVE-2024-26131
Aliases: GHSA-j6pr-fpc8-q9vm
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-26131
Type: osv

## Details
Element Android is an Android Matrix Client. Element Android version 1.4.3 through 1.6.10 is vulnerable to intent redirection, allowing a third-party malicious application to start any internal activity by passing some extra parameters. Possible impact includes making Element Android display an arbitrary web page, executing arbitrary JavaScript; bypassing PIN code protection; and account takeover by spawning a login screen to send credentials to an arbitrary home server. This issue is fixed in Element Android 1.6.12. There is no known workaround to mitigate the issue.

## References
- https://support.google.com/faqs/answer/9267555?hl=en
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26131.json
- https://github.com/element-hq/element-android/security/advisories/GHSA-j6pr-fpc8-q9vm
- https://nvd.nist.gov/vuln/detail/CVE-2024-26131
- https://github.com/element-hq/element-android/commit/53734255ec270b0814946350787393dfcaa2a5a9
- https://element.io/blog/security-release-element-android-1-6-12
