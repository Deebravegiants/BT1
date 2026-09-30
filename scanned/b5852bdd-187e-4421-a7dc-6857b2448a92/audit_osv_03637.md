# [H] ALPINE-CVE-2026-35385

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-35385
Ecosystem: Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-35385
Type: osv

## Affected
- Alpine:v3.24: `dropbear` — affected >=0 <2026.91-r0

## Details
In OpenSSH before 10.3, a file downloaded by scp may be installed setuid or setgid, an outcome contrary to some users' expectations, if the download is performed as root with -O (legacy scp protocol) and without -p (preserve mode).

## References
- https://security.alpinelinux.org/vuln/CVE-2026-35385
