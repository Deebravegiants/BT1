# [H] ksmbd: prevent connection release during oplock break notification

## Summary
Severity: High
Advisory: CVE-2025-21955
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21955
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: prevent connection release during oplock break notification

ksmbd_work could be freed when after connection release.
Increment r_count of ksmbd_conn to indicate that requests
are not finished yet and to not release the connection.

## References
- https://git.kernel.org/stable/c/09aeab68033161cb54f194da93e51a11aee6144b
- https://git.kernel.org/stable/c/3aa660c059240e0c795217182cf7df32909dd917
- https://git.kernel.org/stable/c/a4261bbc33fbf99b99c80aa3a2c5097611802980
- https://git.kernel.org/stable/c/f17d1c63a76b0fe8e9c78023a86507a3a6d62cfa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21955.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21955
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
