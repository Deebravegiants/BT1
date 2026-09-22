# [H] wifi: ieee80211: validate MLE common info length

## Summary
Severity: High
Advisory: CVE-2026-68471
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68471
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ieee80211: validate MLE common info length

ieee80211_mle_common_size() uses the first common-info octet as the
common information length for all known MLE types. However,
ieee80211_mle_size_ok() only validates that octet for Basic, Probe
Request, and TDLS MLEs.

Reconfiguration MLEs also skipped the length octet when calculating the
minimum common size, and Priority Access MLEs skipped validation of the
advertised common information length.

Account for the Reconfiguration common-info length octet and validate
the advertised common information length for all known MLE types. Keep
unknown-type handling unchanged.

[remove now misleading comment]

## References
- https://git.kernel.org/stable/c/293baeae9b2434a3e432629d7720b5603db2d77e
- https://git.kernel.org/stable/c/2b1589fd9a076727a73bfb39e96622a76415ad32
- https://git.kernel.org/stable/c/90576bd6921a91eb038bffbb4b9467c2dc26aa1d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68471.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68471
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
