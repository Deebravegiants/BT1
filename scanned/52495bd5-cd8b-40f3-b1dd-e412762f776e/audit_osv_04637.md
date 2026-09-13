# [H] Regular expression Denial of Service in dialog plugin

## Summary
Severity: High
Advisory: BIT-drupal-2022-24729
Aliases: BIT-drupal-2022-24728, CVE-2022-24728, CVE-2022-24729, DRUPAL-CORE-2022-005, GHSA-4fc4-4p5g-6w89, GHSA-f6rf-9m92-x2hh
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-drupal-2022-24729
Type: osv

## Affected
- Bitnami: `drupal` — affected >=9.3.0 <9.3.8

## Details
CKEditor4 is an open source what-you-see-is-what-you-get HTML editor. CKEditor4 prior to version 4.18.0 contains a vulnerability in the `dialog` plugin. The vulnerability allows abuse of a dialog input validator regular expression, which can cause a significant performance drop resulting in a browser tab freeze. A patch is available in version 4.18.0. There are currently no known workarounds.

## References
- https://ckeditor.com/cke4/release/CKEditor-4.18.0
- https://github.com/ckeditor/ckeditor4/security/advisories/GHSA-f6rf-9m92-x2hh
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VR76VBN5GW5QUBJFHVXRX36UZ6YTCMW6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WOZGMCYDB2OKKULFXZKM6V7JJW4ZZHJP/
- https://www.drupal.org/sa-core-2022-005
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-24729
