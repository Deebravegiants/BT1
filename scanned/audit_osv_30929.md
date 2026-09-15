# [H] dlm: fix dlm_recover_members refcount on error

## Summary
Severity: High
Advisory: CVE-2024-56749
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56749
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

dlm: fix dlm_recover_members refcount on error

If dlm_recover_members() fails we don't drop the references of the
previous created root_list that holds and keep all rsbs alive during the
recovery. It might be not an unlikely event because ping_members() could
run into an -EINTR if another recovery progress was triggered again.

## References
- https://git.kernel.org/stable/c/200b977ebbc313a59174ba971006a231b3533dc5
- https://git.kernel.org/stable/c/3230718a75a6c30ed60ac920c26be2119fa82b8e
- https://git.kernel.org/stable/c/fb2ec564887af1f365d754f7c306f1b5cd375b5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56749.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56749
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
