# [H] CVE-2021-26826

## Summary
Severity: High
Advisory: CVE-2021-26826
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-26826
Type: osv

## Details
A stack overflow issue exists in Godot Engine up to v3.2 and is caused by improper boundary checks when loading .TGA image files. Depending on the context of the application, attack vector can be local or remote, and can lead to code execution and/or system crash.

## References
- https://github.com/godotengine/godot/pull/45701
- https://github.com/godotengine/godot/pull/45701/commits/403e4fd08b0b212e96f53d926e6273e0745eaa5a
