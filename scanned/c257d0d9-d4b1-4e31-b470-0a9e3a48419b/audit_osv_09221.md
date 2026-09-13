# [M] CVE-2016-9086

## Summary
Severity: Medium
Advisory: CVE-2016-9086
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-11-03
Source: https://osv.dev/vulnerability/CVE-2016-9086
Type: osv

## Details
GitLab versions 8.9.x and above contain a critical security flaw in the "import/export project" feature of GitLab. Added in GitLab 8.9, this feature allows a user to export and then re-import their projects as tape archive files (tar). All GitLab versions prior to 8.13.0 restricted this feature to administrators only. Starting with version 8.13.0 this feature was made available to all users. This feature did not properly check for symbolic links in user-provided archives and therefore it was possible for an authenticated user to retrieve the contents of any file accessible to the GitLab service account. This included sensitive files such as those that contain secret tokens used by the GitLab service to authenticate users. GitLab CE and EE versions 8.13.0 through 8.13.2, 8.12.0 through 8.12.7, 8.11.0 through 8.11.10, 8.10.0 through 8.10.12, and 8.9.0 through 8.9.11 are affected.

## References
- http://www.securityfocus.com/bid/94136
- https://about.gitlab.com/2016/11/02/cve-2016-9086-patches/
