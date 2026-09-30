# [H] Kinto Attachment's attachments can be replaced on read-only records

## Summary
Severity: High
Advisory: GHSA-hvp4-vrv2-8wrq
CVE: CVE-2024-1314
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-hvp4-vrv2-8wrq
Type: github-advisory

## Affected
- PyPI: `kinto-attachment` — affected >=0 <6.4.0

## Details
### Impact

The attachment file of an existing record can be replaced if the user has `"read"` permission on one of the parent (collection or bucket).

And if the `"read"` permission is given to `"system.Everyone"` on one of the parent, then the attachment can be replaced on a record using an anonymous request.

Note that if the parent has no explicit read permission, then the records attachments are safe.

### Patches

- Patch released in kinto-attachment 6.4.0
- https://github.com/Kinto/kinto-attachment/commit/f4a31484f5925cbc02b59ebd37554538ab826ca1

### Workarounds

None if the read permission has to remain granted.

Updating to 6.4.0 or applying the patch individually (if updating is not feasible) is strongly recommended.

### References

- https://bugzilla.mozilla.org/show_bug.cgi?id=1879034

## References
- https://github.com/Kinto/kinto-attachment/security/advisories/GHSA-hvp4-vrv2-8wrq
- https://github.com/Kinto/kinto-attachment/commit/f4a31484f5925cbc02b59ebd37554538ab826ca1
- https://bugzilla.mozilla.org/show_bug.cgi?id=1879034
- https://github.com/Kinto/kinto-attachment
