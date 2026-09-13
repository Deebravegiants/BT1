# [H] ethtool: cmis: require exact CDB reply length

## Summary
Severity: High
Advisory: CVE-2026-63996
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63996
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethtool: cmis: require exact CDB reply length

Malicious SFP module could respond with rpl_len longer than
what cmis_cdb_process_reply() expected, leading to OOB writes.
Malicious HW is a bit theoretical but some modules may just
be buggy and/or the reads may occasionally get corrupted,
so let's protect the kernel.

The existing check protects from short replies. We need to
protect from long ones, too. All callers that pass a non-zero
rpl_exp_len cast the reply payload to a fixed-layout struct
and read fields at fixed offsets, with no version negotiation
or short-reply handling:

  - cmis_cdb_validate_password()
  - cmis_cdb_module_features_get()
  - cmis_fw_update_fw_mng_features_get()

so let's assume that responses longer than expected do not
have to be handled gracefully here. Add a warning message
to make the debug easier in case my understanding is wrong...

Note that page_data->length (argument of kmalloc) comes from
last arg to ethtool_cmis_page_init() which is rpl_exp_len.

Note2 that AIs also like to point out overflows in args->req.payload
itself (which is a fixed-size 120 B buffer, on the stack),
but callers should be reading structs defined by the standard,
so protecting from requests for more data than max seem like
defensive programming.

## References
- https://git.kernel.org/stable/c/2f818cc98fd2c63a08239cb48995f6c3bfe9d9b3
- https://git.kernel.org/stable/c/4d42fb88ec61f2e98c33a9e3a2de371d5edbc6b1
- https://git.kernel.org/stable/c/6c3f999a9d1338c6c89a9ff4549eafe72bc2e7b1
- https://git.kernel.org/stable/c/eb5dcd740cd7fa27bc2caeff2d28ef28e93ff4d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63996.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63996
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
