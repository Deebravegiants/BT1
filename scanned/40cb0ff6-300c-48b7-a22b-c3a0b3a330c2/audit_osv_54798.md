# [M] CVE-2024-43168

## Summary
Severity: Medium
Advisory: CVE-2024-43168
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-43168
Type: osv

## Details
DISPUTE NOTE: this issue does not pose a security risk as it (according to analysis by the original software developer, NLnet Labs) falls within the expected functionality and security controls of the application. Red Hat has made a claim that there is a security risk within Red Hat products. NLnet Labs has no further information about the claim, and suggests that affected Red Hat customers refer to available Red Hat documentation or support channels. ORIGINAL DESCRIPTION: A heap-buffer-overflow flaw was found in the cfg_mark_ports function within Unbound's config_file.c, which can lead to memory corruption. This issue could allow an attacker with local access to provide specially crafted input, potentially causing the application to crash or allowing arbitrary code execution. This could result in a denial of service or unauthorized actions on the system.

## References
- https://github.com/NLnetLabs/unbound/pull/1040/files
- https://lists.debian.org/debian-lts-announce/2024/09/msg00046.html
- https://access.redhat.com/security/cve/CVE-2024-43168
- https://bugzilla.redhat.com/show_bug.cgi?id=2303462
- https://github.com/NLnetLabs/unbound/issues/1039
