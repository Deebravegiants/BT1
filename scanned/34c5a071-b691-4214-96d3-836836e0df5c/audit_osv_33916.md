# [M] Kanboard vulnerable to Username Enumeration via Login Behavior and Bruteforce Protection Bypass

## Summary
Severity: Medium
Advisory: CVE-2025-52576
Aliases: GHSA-qw57-7cx6-wvp7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-52576
Type: osv

## Details
Kanboard is project management software that focuses on the Kanban methodology. Prior to version 1.2.46, Kanboard is vulnerable to username enumeration and IP spoofing-based brute-force protection bypass. By analyzing login behavior and abusing trusted HTTP headers, an attacker can determine valid usernames and circumvent rate-limiting or blocking mechanisms. Any organization running a publicly accessible Kanboard instance is affected, especially if relying on IP-based protections like Fail2Ban or CAPTCHA for login rate-limiting. Attackers with access to the login page can exploit this flaw to enumerate valid usernames and bypass IP-based blocking mechanisms, putting all user accounts at higher risk of brute-force or credential stuffing attacks. Version 1.2.46 contains a patch for the issue.

## References
- https://github.com/kanboard/kanboard/blob/cbb7e60fb595ff4572bb8801b275a0b451c4bda0/app/Model/UserLockingModel.php#L101-L104
- https://github.com/kanboard/kanboard/blob/cbb7e60fb595ff4572bb8801b275a0b451c4bda0/app/Subscriber/AuthSubscriber.php#L96-L108
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52576.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-qw57-7cx6-wvp7
- https://nvd.nist.gov/vuln/detail/CVE-2025-52576
- https://github.com/kanboard/kanboard/commit/3079623640dc39f9c7b0c840d2a79095331051f1
