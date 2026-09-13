# [H] CVE-2024-52867

## Summary
Severity: High
Advisory: CVE-2024-52867
CVSS: 8.1 (CVSS:3.1/AC:H/AV:L/A:H/C:H/I:H/PR:N/S:C/UI:N)
Published: 2024-11-17
Source: https://osv.dev/vulnerability/CVE-2024-52867
Type: osv

## Details
guix-daemon in GNU Guix before 5ab3c4c allows privilege escalation because build outputs are accessible by local users before file metadata concerns (e.g., for setuid and setgid programs) are properly addressed. The vulnerability can be remediated within the product via certain pull, reconfigure, and restart actions. Both 5ab3c4c and 5582241 are needed to resolve the vulnerability.

## References
- https://git.savannah.gnu.org/cgit/guix.git/commit/?id=558224140dab669cabdaebabff18504a066c48d4
- https://git.savannah.gnu.org/cgit/guix.git/commit/?id=5ab3c4c1e43ebb637551223791db0ea3519986e1
- https://lists.debian.org/debian-lts-announce/2024/11/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52867.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52867
- https://guix.gnu.org/en/blog/2024/build-user-takeover-vulnerability/
