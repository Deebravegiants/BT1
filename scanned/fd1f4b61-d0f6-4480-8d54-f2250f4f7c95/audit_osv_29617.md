# [H] smb/client: avoid possible NULL dereference in cifs_free_subrequest()

## Summary
Severity: High
Advisory: CVE-2024-44992
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44992
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/client: avoid possible NULL dereference in cifs_free_subrequest()

Clang static checker (scan-build) warning:
	cifsglob.h:line 890, column 3
	Access to field 'ops' results in a dereference of a null pointer.

Commit 519be989717c ("cifs: Add a tracepoint to track credits involved in
R/W requests") adds a check for 'rdata->server', and let clang throw this
warning about NULL dereference.

When 'rdata->credits.value != 0 && rdata->server == NULL' happens,
add_credits_and_wake_if() will call rdata->server->ops->add_credits().
This will cause NULL dereference problem. Add a check for 'rdata->server'
to avoid NULL dereference.

## References
- https://git.kernel.org/stable/c/74c2ab6d653b4c2354df65a7f7f2df1925a40a51
- https://git.kernel.org/stable/c/fead60a6d5f84b472b928502a42c419253afe6c1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44992.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44992
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
