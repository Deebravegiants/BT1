# [C] KVM: SEV: Ignore Port I/O requests of length '0'

## Summary
Severity: Critical
Advisory: CVE-2026-63940
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63940
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <6.12.95, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SEV: Ignore Port I/O requests of length '0'

Explicitly ignore Port I/O requests of length '0' (or count '0'), so that
setting up the software scratch area (and other code) doesn't have to
worry about underflowing the length, and to allow for WARNing on trying
to configure the scratch area with len==0.

## References
- https://git.kernel.org/stable/c/2254972d4d69e279ba4e87bf0968eb08ad0d3c92
- https://git.kernel.org/stable/c/3988bd2723de407ae90fa7a6f6029b4e60238c58
- https://git.kernel.org/stable/c/3b6035bc6bff20e89752ce4358bc4c9a9d5883f2
- https://git.kernel.org/stable/c/c30cde934c7813b4e3069765dac64ce3d31e34f2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63940.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63940
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
