# [H] tee: amdtee: fix race condition in amdtee_open_session

## Summary
Severity: High
Advisory: CVE-2023-53047
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53047
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.177, >=5.11.0 <5.15.105, >=5.16.0 <6.1.22, >=6.2.0 <6.2.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tee: amdtee: fix race condition in amdtee_open_session

There is a potential race condition in amdtee_open_session that may
lead to use-after-free. For instance, in amdtee_open_session() after
sess->sess_mask is set, and before setting:

    sess->session_info[i] = session_info;

if amdtee_close_session() closes this same session, then 'sess' data
structure will be released, causing kernel panic when 'sess' is
accessed within amdtee_open_session().

The solution is to set the bit sess->sess_mask as the last step in
amdtee_open_session().

## References
- https://git.kernel.org/stable/c/02b296978a2137d7128151c542e84dc96400bc00
- https://git.kernel.org/stable/c/a63cce9393e4e7dbc5af82dc87e68cb321cb1a78
- https://git.kernel.org/stable/c/b3ef9e6fe09f1a132af28c623edcf4d4f39d9f35
- https://git.kernel.org/stable/c/f632a90f8e39db39b322107b9a8d438b826a7f4f
- https://git.kernel.org/stable/c/f8502fba45bd30e1a6a354d9d898bc99d1a11e6d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53047.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53047
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
