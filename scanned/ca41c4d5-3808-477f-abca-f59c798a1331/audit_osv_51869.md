# [C] CVE-2021-43529

## Summary
Severity: Critical
Advisory: CVE-2021-43529
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-16
Source: https://osv.dev/vulnerability/CVE-2021-43529
Type: osv

## Details
Thunderbird versions prior to 91.3.0 are vulnerable to the heap overflow described in CVE-2021-43527 when processing S/MIME messages. Thunderbird versions 91.3.0 and later will not call the vulnerable code when processing S/MIME messages that contain certificates with DER-encoded DSA or RSA-PSS signatures.

## References
- https://bugzilla.mozilla.org/show_bug.cgi?id=CVE-2021-43529
