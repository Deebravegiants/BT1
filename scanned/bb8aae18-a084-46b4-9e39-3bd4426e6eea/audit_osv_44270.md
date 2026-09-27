# [H] s390/zcrypt: Fix wrong domain value verification with EP11 CPRBs

## Summary
Severity: High
Advisory: CVE-2026-80709
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80709
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/zcrypt: Fix wrong domain value verification with EP11 CPRBs

There is a wrong upper limit check for the domain value when an EP11
CPRB is processed for sending to a crypto card. This check is only
active on custom device nodes but may lead to access heap memory
behind perms->adm when an administrative CPRB is sent.
Add correct limit (AP_DOMAINS = 256) checking to fix this.

## References
- https://git.kernel.org/stable/c/1223477ca88e2396eca440919d0ca8754df79bd5
- https://git.kernel.org/stable/c/13e53d6ae1c3b2ff1be75b9ef09be26f4ec3ce15
- https://git.kernel.org/stable/c/4589f742718d0256ea6dd1f5a78be6e689bdb8aa
- https://git.kernel.org/stable/c/672b12940e3f1336dfed5287412a71500adf2a76
- https://git.kernel.org/stable/c/983279d7f86ade73db86f886e09172dd567031b5
- https://git.kernel.org/stable/c/b505dcc8307d64468b463dfad45a03bf865c637e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80709.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80709
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
