# [C] Stalwart Mail Server has privilege escalation by design

## Summary
Severity: Critical
Advisory: CVE-2024-35187
Aliases: GHSA-rwp5-f854-ppg6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/CVE-2024-35187
Type: osv

## Details
Stalwart Mail Server is an open-source mail server. Prior to version 0.8.0, attackers who achieved Arbitrary Code Execution as the stalwart-mail user (including web interface admins) can gain complete root access to the system. Usually, system services are run as a separate user (not as root) to isolate an attacker with Arbitrary Code Execution to the current service. Therefore, other system services and the system itself remains protected in case of a successful attack. stalwart-mail runs as a separate user, but it can give itself full privileges again in a simple way, so this protection is practically ineffective. Server admins who handed out the admin credentials to the mail server, but didn't want to hand out complete root access to the system, as well as any attacked user when the attackers gained Arbitrary Code Execution using another vulnerability, may be vulnerable. Version 0.8.0 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35187.json
- https://github.com/stalwartlabs/mail-server/security/advisories/GHSA-rwp5-f854-ppg6
- https://nvd.nist.gov/vuln/detail/CVE-2024-35187
