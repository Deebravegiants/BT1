# [C] CVE-2021-37595

## Summary
Severity: Critical
Advisory: CVE-2021-37595
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-37595
Type: osv

## Details
In FreeRDP before 2.4.0 on Windows, wf_cliprdr_server_file_contents_request in client/Windows/wf_cliprdr.c has missing input checks for a FILECONTENTS_RANGE File Contents Request PDU.

## References
- https://github.com/FreeRDP/FreeRDP/compare/2.3.2...2.4.0
- https://github.com/FreeRDP/FreeRDP/commit/0d79670a28c0ab049af08613621aa0c267f977e9
