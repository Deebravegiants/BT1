# [C] CVE-2011-3145

## Summary
Severity: Critical
Advisory: CVE-2011-3145
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2011-3145
Type: osv

## Details
When mount.ecrpytfs_private before version 87-0ubuntu1.2 calls setreuid() it doesn't also set the effective group id. So when it creates the new version, mtab.tmp, it's created with the group id of the user running mount.ecryptfs_private.

## References
- http://bazaar.launchpad.net/~ecryptfs/ecryptfs/trunk/revision/558
- http://bazaar.launchpad.net/~ecryptfs/ecryptfs/trunk/revision/558
