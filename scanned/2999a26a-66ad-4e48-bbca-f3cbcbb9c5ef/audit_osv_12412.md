# [C] CVE-2018-11743

## Summary
Severity: Critical
Advisory: CVE-2018-11743
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2018-11743
Type: osv

## Details
The init_copy function in kernel.c in mruby 1.4.1 makes initialize_copy calls for TT_ICLASS objects, which allows attackers to cause a denial of service (mrb_hash_keys uninitialized pointer and application crash) or possibly have unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00006.html
- https://github.com/mruby/mruby/commit/b64ce17852b180dfeea81cf458660be41a78974d
- https://github.com/mruby/mruby/issues/4027
