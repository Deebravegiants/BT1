# [M] Libtpms: libtpms: heap out-of-bounds read in tpm2 state unmarshalling via unchecked block_skip_read() blocksize

## Summary
Severity: Medium
Advisory: CVE-2026-85769
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85769
Type: osv

## Details
A flaw was found in libtpms, a library that provides software TPM 2.0 emulation. When restoring TPM 2.0 state (for example during a virtual machine's power-on or state/migration restore), a malformed state blob can supply an oversized skip-block length that is not validated against the remaining size of the input buffer. This can drive an internal size counter negative, which bypasses a subsequent bounds check due to an unsafe signed-to-unsigned conversion, causing the parser to read memory outside the bounds of the heap buffer holding the state data. Successful exploitation can crash the process hosting libtpms (such as swtpm), resulting in a denial of service of the emulated TPM device and the virtual machine that depends on it. No data corruption or information disclosure was confirmed.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-85769
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85769.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85769
- https://bugzilla.redhat.com/show_bug.cgi?id=2528538
- https://github.com/stefanberger/libtpms/issues/614
- https://github.com/stefanberger/libtpms/commit/b1462888180d896af03cae0487e8d45009cc445e
- https://github.com/stefanberger/libtpms/pull/613
