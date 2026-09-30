# [H] mailcow is vulnerable to shell command injection via xoauth2 authentication in imapsync​

## Summary
Severity: High
Advisory: CVE-2023-26490
Aliases: GHSA-3j2f-wf52-cjg7
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-03-03
Source: https://osv.dev/vulnerability/CVE-2023-26490
Type: osv

## Details
mailcow is a dockerized email package, with multiple containers linked in one bridged network. The Sync Job feature - which can be made available to standard users by assigning them the necessary permission - suffers from a shell command injection. A malicious user can abuse this vulnerability to obtain shell access to the Docker container running dovecot. The imapsync Perl script implements all the necessary functionality for this feature, including the XOAUTH2 authentication mechanism. This code path creates a shell command to call openssl. However, since different parts of the specified user password are included without any validation, one can simply execute additional shell commands. Notably, the default ACL for a newly-created mailcow account does not include the necessary permission. The Issue has been fixed within the 2023-03 Update (March 3rd 2023). As a temporary workaround the Syncjob ACL can be removed from all mailbox users, preventing from creating or changing existing Syncjobs.

## References
- https://github.com/mailcow/mailcow-dockerized/releases/tag/2023-03
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26490.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-3j2f-wf52-cjg7
- https://nvd.nist.gov/vuln/detail/CVE-2023-26490
