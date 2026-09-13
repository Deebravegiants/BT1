# [H] apparmor: Fix double free of ns_name in aa_replace_profiles()

## Summary
Severity: High
Advisory: CVE-2026-23408
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-23408
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.18, >=6.19.0 <6.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: Fix double free of ns_name in aa_replace_profiles()

if ns_name is NULL after
1071         error = aa_unpack(udata, &lh, &ns_name);

and if ent->ns_name contains an ns_name in
1089                 } else if (ent->ns_name) {

then ns_name is assigned the ent->ns_name
1095                         ns_name = ent->ns_name;

however ent->ns_name is freed at
1262                 aa_load_ent_free(ent);

and then again when freeing ns_name at
1270         kfree(ns_name);

Fix this by NULLing out ent->ns_name after it is transferred to ns_name

")

## References
- https://git.kernel.org/stable/c/18b5233e860c294a847ee07869d93c0b8673a54b
- https://git.kernel.org/stable/c/35f4caec1352054b9a61cfdf2bf1898073637aa0
- https://git.kernel.org/stable/c/55ef2af7490aaf72f8ffe11ec44c6bcb7eb2162a
- https://git.kernel.org/stable/c/5df0c44e8f5f619d3beb871207aded7c78414502
- https://git.kernel.org/stable/c/7998ab3010d2317643f91828f1853d954ef31387
- https://git.kernel.org/stable/c/86feeccd6b93ed94bd6655f30de80f163f8d5a45
- https://git.kernel.org/stable/c/c053ae381ce227577567d1ef10090ce7506d7a28
- https://git.kernel.org/stable/c/c6347a2116ecccb8fd9ee4ebc75ae41d1d7ef689
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23408.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
