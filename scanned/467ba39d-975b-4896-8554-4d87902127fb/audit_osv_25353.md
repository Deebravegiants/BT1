# [H] Grav Server-side Template Injection via Insufficient Validation in filterFilter

## Summary
Severity: High
Advisory: CVE-2023-34252
Aliases: GHSA-96xv-rmwj-6p9w
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-14
Source: https://osv.dev/vulnerability/CVE-2023-34252
Type: osv

## Details
Grav is a flat-file content management system. Prior to version 1.7.42, there is a logic flaw in the `GravExtension.filterFilter()` function whereby validation against a denylist of unsafe functions is only performed when the argument passed to filter is a string. However, passing an array as a callable argument allows the validation check to be skipped. Consequently, a low privileged attacker with login access to Grav Admin panel and page creation/update permissions is able to inject malicious templates to obtain remote code execution. The vulnerability can be found in the `GravExtension.filterFilter()` function declared in `/system/src/Grav/Common/Twig/Extension/GravExtension.php`. Version 1.7.42 contains a patch for this issue. End users should also ensure that `twig.undefined_functions` and `twig.undefined_filters` properties in `/path/to/webroot/system/config/system.yaml` configuration file are set to `false` to disallow Twig from treating undefined filters/functions as PHP functions and executing them.

## References
- https://github.com/getgrav/grav/blob/1.7.40/system/src/Grav/Common/Twig/Extension/GravExtension.php#L1692-L1698
- https://github.com/getgrav/grav/blob/1.7.40/system/src/Grav/Common/Utils.php#L1956-L2074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34252.json
- https://github.com/getgrav/grav/security/advisories/GHSA-96xv-rmwj-6p9w
- https://nvd.nist.gov/vuln/detail/CVE-2023-34252
- https://github.com/getgrav/grav/commit/244758d4383034fe4cd292d41e477177870b65ec
