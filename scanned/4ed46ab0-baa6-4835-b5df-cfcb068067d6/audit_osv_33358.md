# [H] net/sctp: fix a null dereference in sctp_disposition sctp_sf_do_5_1D_ce()

## Summary
Severity: High
Advisory: CVE-2025-40187
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40187
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sctp: fix a null dereference in sctp_disposition sctp_sf_do_5_1D_ce()

If new_asoc->peer.adaptation_ind=0 and sctp_ulpevent_make_authkey=0
and sctp_ulpevent_make_authkey() returns 0, then the variable
ai_ev remains zero and the zero will be dereferenced
in the sctp_ulpevent_free() function.

## References
- https://git.kernel.org/stable/c/025419f4e216a3ae0d0cec622262e98e8078c447
- https://git.kernel.org/stable/c/1014b83778c8677f1d7a57c26dc728baa801ac62
- https://git.kernel.org/stable/c/2f3119686ef50319490ccaec81a575973da98815
- https://git.kernel.org/stable/c/7f702f85df0266ed7b5bab81ba50394c92f3c928
- https://git.kernel.org/stable/c/badbd79313e6591616c1b78e29a9b71efed7f035
- https://git.kernel.org/stable/c/c21f45cfa4a9526b34d76b397c9ef080668b6e73
- https://git.kernel.org/stable/c/d0e8f1445c19b1786759ba72a38267e1449bab7e
- https://git.kernel.org/stable/c/dbceedc0213e75bf3e9f9f9e2f66b10699d004fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40187.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40187
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
