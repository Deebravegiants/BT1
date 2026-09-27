# [H] GHSL-2023-136_Samson

## Summary
Severity: High
Advisory: CVE-2024-42363
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-20
Source: https://osv.dev/vulnerability/CVE-2024-42363
Type: osv

## Details
Prior to 3385, the user-controlled role parameter enters the application in the Kubernetes::RoleVerificationsController. The role parameter flows into the RoleConfigFile initializer and then into the Kubernetes::Util.parse_file method where it is unsafely deserialized using the YAML.load_stream method. This issue may lead to Remote Code Execution (RCE). This vulnerability is fixed in 3385.

## References
- https://github.com/zendesk/samson/blob/107efb4a252425966aac5e77d0c3670f9b5d7229/plugins/kubernetes/app/controllers/kubernetes/role_verifications_controller.rb#L10
- https://github.com/zendesk/samson/blob/107efb4a252425966aac5e77d0c3670f9b5d7229/plugins/kubernetes/app/controllers/kubernetes/role_verifications_controller.rb#L7
- https://github.com/zendesk/samson/blob/107efb4a252425966aac5e77d0c3670f9b5d7229/plugins/kubernetes/app/models/kubernetes/role_config_file.rb#L80
- https://github.com/zendesk/samson/blob/107efb4a252425966aac5e77d0c3670f9b5d7229/plugins/kubernetes/app/models/kubernetes/util.rb#L9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42363.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42363
- https://securitylab.github.com/advisories/GHSL-2023-136_Samson/
- https://github.com/zendesk/samson/pull/4071
