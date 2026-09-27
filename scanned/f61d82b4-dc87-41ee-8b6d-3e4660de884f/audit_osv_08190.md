# [M] CVE-2016-15006

## Summary
Severity: Medium
Advisory: CVE-2016-15006
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-01-02
Source: https://osv.dev/vulnerability/CVE-2016-15006
Type: osv

## Details
A vulnerability, which was classified as problematic, has been found in enigmaX up to 2.2. This issue affects the function getSeed of the file main.c of the component Scrambling Table Handler. The manipulation leads to predictable seed in pseudo-random number generator (prng). The attack may be initiated remotely. The complexity of an attack is rather high. The exploitation is known to be difficult. Upgrading to version 2.3 is able to address this issue. The identifier of the patch is 922bf90ca14a681629ba0b807a997a81d70225b5. It is recommended to upgrade the affected component. The identifier VDB-217181 was assigned to this vulnerability.

## References
- https://github.com/pfmonville/enigmaX/releases/tag/2.3
- https://vuldb.com/?ctiid.217181
- https://vuldb.com/?id.217181
- https://github.com/pfmonville/enigmaX/commit/922bf90ca14a681629ba0b807a997a81d70225b5
