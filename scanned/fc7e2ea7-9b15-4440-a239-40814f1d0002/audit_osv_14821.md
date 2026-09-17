# [M] CVE-2019-11690

## Summary
Severity: Medium
Advisory: CVE-2019-11690
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-05-03
Source: https://osv.dev/vulnerability/CVE-2019-11690
Type: osv

## Details
gen_rand_uuid in lib/uuid.c in Das U-Boot v2014.04 through v2019.04 lacks an srand call, which allows attackers to determine UUID values in scenarios where CONFIG_RANDOM_UUID is enabled, and Das U-Boot is relied upon for UUID values of a GUID Partition Table of a boot device.

## References
- https://patchwork.ozlabs.org/patch/1092945
