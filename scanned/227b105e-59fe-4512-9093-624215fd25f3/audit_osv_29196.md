# [H] wifi: iwlwifi: mvm: check n_ssids before accessing the ssids

## Summary
Severity: High
Advisory: CVE-2024-40929
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40929
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: check n_ssids before accessing the ssids

In some versions of cfg80211, the ssids poinet might be a valid one even
though n_ssids is 0. Accessing the pointer in this case will cuase an
out-of-bound access. Fix this by checking n_ssids first.

## References
- https://git.kernel.org/stable/c/29a18d56bd64b95bd10bda4afda512558471382a
- https://git.kernel.org/stable/c/3c4771091ea8016c8601399078916f722dd8833b
- https://git.kernel.org/stable/c/60d62757df30b74bf397a2847a6db7385c6ee281
- https://git.kernel.org/stable/c/62e007bdeb91c6879a4652c3426aef1cd9d2937b
- https://git.kernel.org/stable/c/9e719ae3abad60e245ce248ba3f08148f375a614
- https://git.kernel.org/stable/c/f777792952d03bbaf8329fdfa99393a5a33e2640
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40929.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40929
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
