# [H] CVE-2019-12439

## Summary
Severity: High
Advisory: CVE-2019-12439
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-29
Source: https://osv.dev/vulnerability/CVE-2019-12439
Type: osv

## Details
bubblewrap.c in Bubblewrap before 0.3.3 misuses temporary directories in /tmp as a mount point. In some particular configurations (related to XDG_RUNTIME_DIR), a local attacker may abuse this flaw to prevent other users from executing bubblewrap or potentially execute code.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00015.html
- https://access.redhat.com/errata/RHSA-2019:1833
- https://github.com/projectatomic/bubblewrap/issues/304
- https://github.com/projectatomic/bubblewrap/releases/tag/v0.3.3
- https://security.gentoo.org/glsa/202006-18
- https://bugzilla.redhat.com/show_bug.cgi?id=1695963
- https://github.com/projectatomic/bubblewrap/commit/efc89e3b939b4bde42c10f065f6b7b02958ed50e
