# [H] hwmon: (coretemp) Fix out-of-bounds memory access

## Summary
Severity: High
Advisory: CVE-2024-26664
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-26664
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.78, >=6.1.0 <6.6.17, >=6.2.0 <6.7.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (coretemp) Fix out-of-bounds memory access

Fix a bug that pdata->cpu_map[] is set before out-of-bounds check.
The problem might be triggered on systems with more than 128 cores per
package.

## References
- https://git.kernel.org/stable/c/1eb74c00c9c3b13cb65e508c5d5a2f11afb96b8b
- https://git.kernel.org/stable/c/3a7753bda55985dc26fae17795cb10d825453ad1
- https://git.kernel.org/stable/c/4e440abc894585a34c2904a32cd54af1742311b3
- https://git.kernel.org/stable/c/853a6503c586a71abf27e60a7f8c4fb28092976d
- https://git.kernel.org/stable/c/93f0f4e846fcb682c3ec436e3b2e30e5a3a8ee6a
- https://git.kernel.org/stable/c/9bce69419271eb8b2b3ab467387cb59c99d80deb
- https://git.kernel.org/stable/c/a16afec8e83c56b14a4a73d2e3fb8eec3a8a057e
- https://git.kernel.org/stable/c/f0da068c75c20ffc5ba28243ff577531dc2af1fd
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26664.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26664
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
