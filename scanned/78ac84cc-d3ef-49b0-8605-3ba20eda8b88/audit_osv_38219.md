# [H] CVE-2026-35385

## Summary
Severity: High
Advisory: CVE-2026-35385
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-35385
Type: osv

## Details
In OpenSSH before 10.3, a file downloaded by scp may be installed setuid or setgid, an outcome contrary to some users' expectations, if the download is performed as root with -O (legacy scp protocol) and without -p (preserve mode).

## References
- https://marc.info/?l=openssh-unix-dev&m=177513443901484&w=2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-35385.json
- https://www.openssh.org/releasenotes.html#10.3p1
- https://www.openwall.com/lists/oss-security/2026/04/02/3
- https://access.redhat.com/errata/RHSA-2026:12389
- https://access.redhat.com/errata/RHSA-2026:13380
- https://access.redhat.com/errata/RHSA-2026:13381
- https://access.redhat.com/errata/RHSA-2026:13383
- https://access.redhat.com/errata/RHSA-2026:14937
- https://access.redhat.com/errata/RHSA-2026:16059
- https://access.redhat.com/errata/RHSA-2026:19069
- https://access.redhat.com/errata/RHSA-2026:19219
- https://access.redhat.com/errata/RHSA-2026:20040
- https://access.redhat.com/errata/RHSA-2026:21275
- https://access.redhat.com/errata/RHSA-2026:21298
- https://access.redhat.com/errata/RHSA-2026:21398
- https://access.redhat.com/errata/RHSA-2026:22329
- https://access.redhat.com/errata/RHSA-2026:22468
- https://access.redhat.com/errata/RHSA-2026:22564
- https://access.redhat.com/errata/RHSA-2026:22648
