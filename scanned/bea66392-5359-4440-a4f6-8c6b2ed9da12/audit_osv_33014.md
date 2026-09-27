# [C] mptcp: plug races between subflow fail and subflow creation

## Summary
Severity: Critical
Advisory: CVE-2025-38552
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38552
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.149, >=6.2.0 <6.6.101, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: plug races between subflow fail and subflow creation

We have races similar to the one addressed by the previous patch between
subflow failing and additional subflow creation. They are just harder to
trigger.

The solution is similar. Use a separate flag to track the condition
'socket state prevent any additional subflow creation' protected by the
fallback lock.

The socket fallback makes such flag true, and also receiving or sending
an MP_FAIL option.

The field 'allow_infinite_fallback' is now always touched under the
relevant lock, we can drop the ONCE annotation on write.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/659da22dee5ff316ba63bdaeeac7b58b5442f6c2
- https://git.kernel.org/stable/c/7c96d519ee15a130842a6513530b4d20acd2bfcd
- https://git.kernel.org/stable/c/c476d627584b7589a134a8b48dd5c6639e4401c5
- https://git.kernel.org/stable/c/def5b7b2643ebba696fc60ddf675dca13f073486
- https://git.kernel.org/stable/c/f81b6fbe13c7fc413b5158cdffc6a59391a2a8db
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38552.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38552
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
