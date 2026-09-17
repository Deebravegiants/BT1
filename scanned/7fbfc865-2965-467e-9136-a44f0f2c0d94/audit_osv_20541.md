# [C] CVE-2021-34813

## Summary
Severity: Critical
Advisory: CVE-2021-34813
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-16
Source: https://osv.dev/vulnerability/CVE-2021-34813
Type: osv

## Details
Matrix libolm before 3.2.3 allows a malicious Matrix homeserver to crash a client (while it is attempting to retrieve an Olm encrypted room key backup from the homeserver) because olm_pk_decrypt has a stack-based buffer overflow. Remote code execution might be possible for some nonstandard build configurations.

## References
- https://gitlab.matrix.org/matrix-org/olm/-/releases/3.2.3
- https://gitlab.matrix.org/matrix-org/olm/-/commit/ccc0d122ee1b4d5e5ca4ec1432086be17d5f901b
- https://matrix.org/blog/2021/06/14/adventures-in-fuzzing-libolm
