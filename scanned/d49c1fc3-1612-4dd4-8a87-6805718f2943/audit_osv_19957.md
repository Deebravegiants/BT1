# [H] CVE-2021-28398

## Summary
Severity: High
Advisory: CVE-2021-28398
Aliases: GHSA-cf8p-c88c-h9jf
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-05
Source: https://osv.dev/vulnerability/CVE-2021-28398
Type: osv

## Details
A privileged attacker in GeoNetwork before 3.12.0 and 4.x before 4.0.4 can use the directory harvester before-script to execute arbitrary OS commands remotely on the hosting infrastructure. A User Administrator or Administrator account is required to perform this. This occurs in the runBeforeScript method in harvesters/src/main/java/org/fao/geonet/kernel/harvest/harvester/localfilesystem/LocalFilesystemHarvester.java. The earliest affected version is 3.4.0.

## References
- https://geonetwork-opensource.org/
- https://github.com/geonetwork/core-geonetwork
- https://geonetwork-opensource.org/manuals/trunk/en/overview/change-log/version-3.6.0.html
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-cf8p-c88c-h9jf
