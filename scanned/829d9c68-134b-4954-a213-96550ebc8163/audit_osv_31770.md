# [H] net/mlx5: HWS, change error flow on matcher disconnect

## Summary
Severity: High
Advisory: CVE-2025-21751
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21751
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.48, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: HWS, change error flow on matcher disconnect

Currently, when firmware failure occurs during matcher disconnect flow,
the error flow of the function reconnects the matcher back and returns
an error, which continues running the calling function and eventually
frees the matcher that is being disconnected.
This leads to a case where we have a freed matcher on the matchers list,
which in turn leads to use-after-free and eventual crash.

This patch fixes that by not trying to reconnect the matcher back when
some FW command fails during disconnect.

Note that we're dealing here with FW error. We can't overcome this
problem. This might lead to bad steering state (e.g. wrong connection
between matchers), and will also lead to resource leakage, as it is
the case with any other error handling during resource destruction.

However, the goal here is to allow the driver to continue and not crash
the machine with use-after-free error.

## References
- https://git.kernel.org/stable/c/1ce840c7a659aa53a31ef49f0271b4fd0dc10296
- https://git.kernel.org/stable/c/23a86c76a1a197e8fbbbd0ce3e826eb58c471624
- https://git.kernel.org/stable/c/5682aad0276ff9b9b0eff3188eb6a1f504d6b436
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21751.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21751
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
