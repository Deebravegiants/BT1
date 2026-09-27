# [H] CVE-2025-52194

## Summary
Severity: High
Advisory: CVE-2025-52194
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-21
Source: https://osv.dev/vulnerability/CVE-2025-52194
Type: osv

## Details
A buffer overflow vulnerability exists in libsndfile version 1.2.2 and potentially earlier versions when processing malformed IRCAM audio files. The vulnerability occurs in the ircam_read_header function at src/ircam.c:164 during sample rate processing, leading to memory corruption and potential code execution.

## References
- https://bushido-sec.com/index.php/2025/08/08/libsndfile-buffer-overflow/
- https://github.com/libsndfile
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52194.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52194
- https://github.com/libsndfile/libsndfile/issues/1082
