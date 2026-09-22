# [H] CVE-2022-43995

## Summary
Severity: High
Advisory: CVE-2022-43995
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-11-02
Source: https://osv.dev/vulnerability/CVE-2022-43995
Type: osv

## Details
Sudo 1.8.0 through 1.9.12, with the crypt() password backend, contains a plugins/sudoers/auth/passwd.c array-out-of-bounds error that can result in a heap-based buffer over-read. This can be triggered by arbitrary local users with access to Sudo by entering a password of seven characters or fewer. The impact could vary depending on the system libraries, compiler, and processor architecture.

## References
- https://news.ycombinator.com/item?id=33465707
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43995.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43995
- https://security.gentoo.org/glsa/202211-08
- https://www.sudo.ws/security/advisories/
- https://bugzilla.redhat.com/show_bug.cgi?id=2139911
- https://github.com/sudo-project/sudo/commit/bd209b9f16fcd1270c13db27ae3329c677d48050
