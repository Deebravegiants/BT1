# [H] wifi: iwlwifi: read txq->read_ptr under lock

## Summary
Severity: High
Advisory: CVE-2024-36922
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36922
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: read txq->read_ptr under lock

If we read txq->read_ptr without lock, we can read the same
value twice, then obtain the lock, and reclaim from there
to two different places, but crucially reclaim the same
entry twice, resulting in the WARN_ONCE() a little later.
Fix that by reading txq->read_ptr under lock.

## References
- https://git.kernel.org/stable/c/43d07103df670484cdd26f9588eabef80f69db89
- https://git.kernel.org/stable/c/aab7b39fcac5f6165f6434bcbb56bb7865d4ad2b
- https://git.kernel.org/stable/c/b83db8e756dec68a950ed2f056248b1704b3deaa
- https://git.kernel.org/stable/c/c2ace6300600c634553657785dfe5ea0ed688ac2
- https://git.kernel.org/stable/c/f30e8af109818c9db08cbcc46eb9713fe4b530ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36922.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36922
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
