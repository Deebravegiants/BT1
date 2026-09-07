# [M] yikes-inc-easy-mailchimp-extender Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-837v-6vgx-jqcc
CVE: CVE-2021-4244
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-837v-6vgx-jqcc
Type: github-advisory

## Affected
- Packagist: `yikesinc/yikes-inc-easy-mailchimp-extender` — affected >=0 <6.8.6

## Details
A vulnerability classified as problematic has been found in yikes-inc-easy-mailchimp-extender Plugin up to 6.8.5. This affects an unknown part of the file admin/partials/ajax/add_field_to_form.php. The manipulation of the argument field_name/merge_tag/field_type/list_id leads to cross site scripting. It is possible to initiate the attack remotely. Upgrading to version 6.8.6 can address this issue. The name of the patch is 3662c6593aa1bb4286781214891d26de2e947695. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-215307.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4244
- https://github.com/EvanHerman/yikes-inc-easy-mailchimp-extender/pull/889
- https://github.com/EvanHerman/yikes-inc-easy-mailchimp-extender/commit/3662c6593aa1bb4286781214891d26de2e947695
- https://github.com/EvanHerman/yikes-inc-easy-mailchimp-extender/releases/tag/6.8.6
- https://github.com/yikesinc/yikes-inc-easy-mailchimp-extender
- https://vuldb.com/?id.215307
