# [H] netfilter: flowtable: validate pppoe header

## Summary
Severity: High
Advisory: CVE-2024-27016
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27016
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.157, >=5.16.0 <6.1.88, >=6.2.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: validate pppoe header

Ensure there is sufficient room to access the protocol field of the
PPPoe header. Validate it once before the flowtable lookup, then use a
helper function to access protocol field.

## References
- https://git.kernel.org/stable/c/87b3593bed1868b2d9fe096c01bcdf0ea86cbebf
- https://git.kernel.org/stable/c/8bf7c76a2a207ca2b4cfda0a279192adf27678d7
- https://git.kernel.org/stable/c/a2471d271042ea18e8a6babc132a8716bb2f08b9
- https://git.kernel.org/stable/c/cf366ee3bc1b7d1c76a882640ba3b3f8f1039163
- https://git.kernel.org/stable/c/d06977b9a4109f8738bb276125eb6a0b772bc433
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27016.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27016
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
