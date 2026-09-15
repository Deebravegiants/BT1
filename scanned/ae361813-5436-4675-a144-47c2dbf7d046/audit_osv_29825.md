# [H] drm/amd/display: Avoid race between dcn35_set_drr() and dc_state_destruct()

## Summary
Severity: High
Advisory: CVE-2024-46850
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46850
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Avoid race between dcn35_set_drr() and dc_state_destruct()

dc_state_destruct() nulls the resource context of the DC state. The pipe
context passed to dcn35_set_drr() is a member of this resource context.

If dc_state_destruct() is called parallel to the IRQ processing (which
calls dcn35_set_drr() at some point), we can end up using already nulled
function callback fields of struct stream_resource.

The logic in dcn35_set_drr() already tries to avoid this, by checking tg
against NULL. But if the nulling happens exactly after the NULL check and
before the next access, then we get a race.

Avoid this by copying tg first to a local variable, and then use this
variable for all the operations. This should work, as long as nobody
frees the resource pool where the timing generators live.

(cherry picked from commit 0607a50c004798a96e62c089a4c34c220179dcb5)

## References
- https://git.kernel.org/stable/c/42850927656a540428e58d370b3c1599a617bac7
- https://git.kernel.org/stable/c/e835d5144f5ef78e4f8828c63e2f0d61144f283a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46850.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46850
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
