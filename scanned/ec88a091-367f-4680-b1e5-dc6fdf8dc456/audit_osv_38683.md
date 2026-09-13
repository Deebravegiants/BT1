# [H] Wazuh: Privilege Escalation via Admin-Protection Bypass in update-user API Endpoint

## Summary
Severity: High
Advisory: CVE-2026-41424
Aliases: GHSA-gj9h-8hmr-xjjr
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-41424
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.9.0 until 4.10.4 and 4.14.6, PUT /security/users/{user_id} in api/api/controllers/security_controller.py passes request.get("user") instead of request.context['token_info']['sub'] as current_user. remove_nones_to_dict() removes the resulting None value, so the reserved-account protection in framework/wazuh/security.py cannot verify who is making the request. An authenticated user with the users_admin role can overwrite the password of protected administrator accounts with user IDs at or below 99, including the wazuh superuser, and gain full administrative control. This issue is fixed in versions 4.10.4 and 4.14.6.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.10.4
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41424.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-gj9h-8hmr-xjjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41424
- https://github.com/wazuh/wazuh/commit/1a38d11574c6d35a4272e1e7145d55d293e7dda4
- https://github.com/wazuh/wazuh/commit/813add3575ecd4df484b2326715ca78f65505b4e
- https://github.com/wazuh/wazuh/pull/35442
- https://github.com/wazuh/wazuh/pull/35469
