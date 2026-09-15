# [H] soundwire: fix enumeration completion

## Summary
Severity: High
Advisory: CVE-2023-54096
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54096
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.190, >=5.11.0 <5.15.126, >=5.16.0 <6.1.43, >=6.2.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

soundwire: fix enumeration completion

The soundwire subsystem uses two completion structures that allow
drivers to wait for soundwire device to become enumerated on the bus and
initialised by their drivers, respectively.

The code implementing the signalling is currently broken as it does not
signal all current and future waiters and also uses the wrong
reinitialisation function, which can potentially lead to memory
corruption if there are still waiters on the queue.

Not signalling future waiters specifically breaks sound card probe
deferrals as codec drivers can not tell that the soundwire device is
already attached when being reprobed. Some codec runtime PM
implementations suffer from similar problems as waiting for enumeration
during resume can also timeout despite the device already having been
enumerated.

## References
- https://git.kernel.org/stable/c/48d1d0ce0782f995fda678508fdae35c5e9593f0
- https://git.kernel.org/stable/c/a36b522767f3a72688893a472e80c9aa03e67eda
- https://git.kernel.org/stable/c/c40d6b3249b11d60e09d81530588f56233d9aa44
- https://git.kernel.org/stable/c/c5265691cd065464d795de5666dcfb89c26b9bc1
- https://git.kernel.org/stable/c/e1d54962a63b6ec04ed0204a3ecca942fde3a6fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54096.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54096
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
