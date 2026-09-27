# [M] Opencast has Incorrect Permission Assignment

## Summary
Severity: Medium
Advisory: GHSA-hx44-c87v-p6xg
CVE: CVE-2017-1000221
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hx44-c87v-p6xg
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-kernel` — affected >=0 <2.2.4

## Details
In Opencast 2.2.3 and older if user names overlap, the Opencast search service used for publication to the media modules and players will handle the access control incorrectly so that users only need to match part of the user name used for the access restriction. For example, a user with the role ROLE_USER will have access to recordings published only for ROLE_USER_X.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000221
- https://github.com/opencast/opencast/commit/f1abcaf998a469a2081461e0e3b4211927849439
- https://opencast.jira.com/browse/MH-11862
