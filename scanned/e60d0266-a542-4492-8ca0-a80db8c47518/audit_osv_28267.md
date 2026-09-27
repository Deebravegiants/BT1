# [H] CVE-2024-30619

## Summary
Severity: High
Advisory: CVE-2024-30619
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-04
Source: https://osv.dev/vulnerability/CVE-2024-30619
Type: osv

## Details
Chamilo LMS Version 1.11.26 is vulnerable to Incorrect Access Control. A non-authenticated attacker can request the number of messages and the number of online users via "/main/inc/ajax/message.ajax.php?a=get_count_message" AND "/main/inc/ajax/online.ajax.php?a=get_users_online."

## References
- https://github.com/bahadoumi/Vulnerability-Research/tree/main/CVE-2024-30619
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30619.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-30619
- https://github.com/chamilo/chamilo-lms/commit/bef68ffe0552cd25b0ef760e582e1188f0f6bf4b
