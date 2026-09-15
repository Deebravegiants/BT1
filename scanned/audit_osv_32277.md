# [M] Tuleap allows default values to be cleared from field configuration

## Summary
Severity: Medium
Advisory: CVE-2025-27094
Aliases: GHSA-r85g-9wjx-pw7f
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-27094
Type: osv

## Details
Tuleap is an open-source suite designed to improve software development management and collaboration. A malicious user with access to a tracker could force-reset certain field configurations, leading to potential information loss. The display time attribute for the date field, the size attribute for the multiselectbox field, the default value, number of rows, and columns attributes for the text field, and the default value, size, and max characters attributes for the string field configurations are lost when added as criteria in a saved report. Additionally, in Tuleap Community Edition versions 16.4.99.1739806825 to 16.4.99.1739877910, this issue could be exploited to prevent access to tracker data by triggering a crash. This vulnerability has been fixed in Tuleap Community Edition 16.4.99.1739877910 and Tuleap Enterprise Edition 16.3-9 and 16.4-4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27094.json
- https://github.com/Enalean/tuleap/commit/ef650abb4a28359a3228d6e1102a742f7c013150
- https://github.com/Enalean/tuleap/security/advisories/GHSA-r85g-9wjx-pw7f
- https://nvd.nist.gov/vuln/detail/CVE-2025-27094
- https://tuleap.net/plugins/tracker/?aid=41849
