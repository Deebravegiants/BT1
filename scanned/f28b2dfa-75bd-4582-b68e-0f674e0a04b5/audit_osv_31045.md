# [M] scsi: megaraid_sas: Fix for a potential deadlock

## Summary
Severity: Medium
Advisory: CVE-2024-57807
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57807
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.289, >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.14.0 <6.1.123, >=5.16.0 <6.6.69, >=6.2.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: megaraid_sas: Fix for a potential deadlock

This fixes a 'possible circular locking dependency detected' warning
      CPU0                    CPU1
      ----                    ----
 lock(&instance->reset_mutex);
                              lock(&shost->scan_mutex);
                              lock(&instance->reset_mutex);
 lock(&shost->scan_mutex);

Fix this by temporarily releasing the reset_mutex.

## References
- https://git.kernel.org/stable/c/3c654998a3e8167a58b6c6fede545fe400a4b554
- https://git.kernel.org/stable/c/466ca39dbf5d0ba71c16b15c27478a9c7d4022a8
- https://git.kernel.org/stable/c/50740f4dc78b41dec7c8e39772619d5ba841ddd7
- https://git.kernel.org/stable/c/78afb9bfad00c4aa58a424111d7edbcab9452f2b
- https://git.kernel.org/stable/c/edadc693bfcc0f1ea08b8fa041c9361fd042410d
- https://git.kernel.org/stable/c/f36d024bd15ed356a80dda3ddc46d0a62aa55815
- https://git.kernel.org/stable/c/f50783148ec98a1d38b87422e2ceaf2380b7b606
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57807.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57807
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
