# [H] CVE-2021-29279

## Summary
Severity: High
Advisory: CVE-2021-29279
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-29279
Type: osv

## Details
There is a integer overflow in function filter_core/filter_props.c:gf_props_assign_value in GPAC 1.0.1. In which, the arg const GF_PropertyValue *value,maybe value->value.data.size is a negative number. In result, memcpy in gf_props_assign_value failed.

## References
- https://github.com/gpac/gpac/commit/da69ad1f970a7e17c865eaec9af98cc84df10d5b
- https://github.com/gpac/gpac/issues/1718
