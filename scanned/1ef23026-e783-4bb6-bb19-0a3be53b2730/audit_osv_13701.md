# [M] CVE-2018-21015

## Summary
Severity: Medium
Advisory: CVE-2018-21015
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2018-21015
Type: osv

## Details
AVC_DuplicateConfig() at isomedia/avc_ext.c in GPAC 0.7.1 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted file. There is "cfg_new->AVCLevelIndication = cfg->AVCLevelIndication;" but cfg could be NULL.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00017.html
- https://github.com/gpac/gpac/issues/1179
