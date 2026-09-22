# [H] CVE-2020-14382

## Summary
Severity: High
Advisory: CVE-2020-14382
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-14382
Type: osv

## Details
A vulnerability was found in upstream release cryptsetup-2.2.0 where, there's a bug in LUKS2 format validation code, that is effectively invoked on every device/image presenting itself as LUKS2 container. The bug is in segments validation code in file 'lib/luks2/luks2_json_metadata.c' in function hdr_validate_segments(struct crypt_device *cd, json_object *hdr_jobj) where the code does not check for possible overflow on memory allocation used for intervals array (see statement "intervals = malloc(first_backup * sizeof(*intervals));"). Due to the bug, library can be *tricked* to expect such allocation was successful but for far less memory then originally expected. Later it may read data FROM image crafted by an attacker and actually write such data BEYOND allocated memory.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OJTQ4KSVCW2NMSU5WFVPOHY46WMNF4OB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TD6YSD63LLRRC4WQ7DJLSXWNUCY6FWBM/
- https://usn.ubuntu.com/4493-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1874712
