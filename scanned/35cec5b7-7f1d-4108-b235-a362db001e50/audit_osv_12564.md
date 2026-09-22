# [C] CVE-2018-12933

## Summary
Severity: Critical
Advisory: CVE-2018-12933
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-28
Source: https://osv.dev/vulnerability/CVE-2018-12933
Type: osv

## Details
PlayEnhMetaFileRecord in enhmetafile.c in Wine 3.7 allows attackers to cause a denial of service (out-of-bounds write) or possibly have unspecified other impact because the attacker controls the pCreatePen->ihPen array index.

## References
- https://bugs.launchpad.net/ubuntu/+source/wine/+bug/1764719
- https://bugs.winehq.org/show_bug.cgi?id=45106
- https://bugs.winehq.org/attachment.cgi?id=61285
- https://source.winehq.org/git/wine.git/commit/8d2676fd14f130f9e8f06744743423168bf8d18d
- https://source.winehq.org/git/wine.git/commit/b6da3547d8990c3c3affc3a5865aefd2a0946949
