# [M] ibmvnic: Free rwi on reset success

## Summary
Severity: Medium
Advisory: CVE-2022-49906
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49906
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ibmvnic: Free rwi on reset success

Free the rwi structure in the event that the last rwi in the list
processed successfully. The logic in commit 4f408e1fa6e1 ("ibmvnic:
retry reset if there are no other resets") introduces an issue that
results in a 32 byte memory leak whenever the last rwi in the list
gets processed.

## References
- https://git.kernel.org/stable/c/535b78739ae75f257c894a05b1afa86ad9a3669e
- https://git.kernel.org/stable/c/c3543a287cfba9105dcc4bb41eb817f51266caaf
- https://git.kernel.org/stable/c/d6dd2fe71153f0ff748bf188bd4af076fe09a0a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49906.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49906
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
