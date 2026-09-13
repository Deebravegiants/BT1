# [H] ovpn: fix NULL dereference when killing missing key

## Summary
Severity: High
Advisory: CVE-2026-80520
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80520
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: fix NULL dereference when killing missing key

ovpn_crypto_kill_key assumes both crypto slots are populated and
dereferences each slot before checking it. That is not guaranteed: a
peer can have only one installed key, and the kill path may be asked to
remove a key that is not present.

Read each slot once while holding the crypto state lock, check for NULL
before looking at key_id, and only replace the slot that actually
matches.

## References
- https://git.kernel.org/stable/c/41d44ac7a61e2f74453af40d4fe1b82af9ea0ada
- https://git.kernel.org/stable/c/a47a080d06ee9d94dc6a2da0fc2b9beeeedb92b3
- https://git.kernel.org/stable/c/acf32a5dff082044cf0fd9492f3c10b7357c15ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80520.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80520
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
