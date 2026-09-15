# [M] wifi: iwlwifi: mvm: fix 6 GHz scan construction

## Summary
Severity: Medium
Advisory: CVE-2024-53055
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53055
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: fix 6 GHz scan construction

If more than 255 colocated APs exist for the set of all
APs found during 2.4/5 GHz scanning, then the 6 GHz scan
construction will loop forever since the loop variable
has type u8, which can never reach the number found when
that's bigger than 255, and is stored in a u32 variable.
Also move it into the loops to have a smaller scope.

Using a u32 there is fine, we limit the number of APs in
the scan list and each has a limit on the number of RNR
entries due to the frame size. With a limit of 1000 scan
results, a frame size upper bound of 4096 (really it's
more like ~2300) and a TBTT entry size of at least 11,
we get an upper bound for the number of ~372k, well in
the bounds of a u32.

## References
- https://git.kernel.org/stable/c/2ac15e5a8f42fed5d90ed9e1197600913678c50f
- https://git.kernel.org/stable/c/2ccd5badadab2d586e91546bf5af3deda07fef1f
- https://git.kernel.org/stable/c/7245012f0f496162dd95d888ed2ceb5a35170f1a
- https://git.kernel.org/stable/c/cde8a7eb5c6762264ff0f4433358e0a0d250c875
- https://git.kernel.org/stable/c/fc621e7a043de346c33bd7ae7e2e0c651d6152ef
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53055.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53055
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
