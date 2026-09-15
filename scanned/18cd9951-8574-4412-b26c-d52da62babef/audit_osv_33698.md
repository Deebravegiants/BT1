# [H] MyBB's upgrade component vulnerable to local file inclusion

## Summary
Severity: High
Advisory: CVE-2025-48940
Aliases: GHSA-q4jv-xwjx-37cp
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-02
Source: https://osv.dev/vulnerability/CVE-2025-48940
Type: osv

## Details
MyBB is free and open source forum software. Prior to version 1.8.39, the upgrade component does not validate user input properly, which allows attackers to perform local file inclusion (LFI) via a specially crafted parameter value. In order to exploit the vulnerability, the installer must be unlocked (no `install/lock` file present) and the upgrade script must be accessible (by re-installing the forum via access to `install/index.php`; when the forum has not yet been installed; or the attacker is authenticated as a forum administrator). MyBB 1.8.39 resolves this issue.

## References
- https://mybb.com/versions/1.8.39
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48940.json
- https://github.com/mybb/mybb/security/advisories/GHSA-q4jv-xwjx-37cp
- https://nvd.nist.gov/vuln/detail/CVE-2025-48940
- https://github.com/mybb/mybb/commit/6e6cfbd524d9101b51e1278ecf520479b64b0f00
