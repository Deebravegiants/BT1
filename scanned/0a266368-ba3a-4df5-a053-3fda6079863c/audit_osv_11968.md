# [H] CVE-2018-1000224

## Summary
Severity: High
Advisory: CVE-2018-1000224
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000224
Type: osv

## Details
Godot Engine version All versions prior to 2.1.5, all 3.0 versions prior to 3.0.6. contains a Signed/unsigned comparison, wrong buffer size chackes, integer overflow, missing padding initialization vulnerability in (De)Serialization functions (core/io/marshalls.cpp) that can result in DoS (packet of death), possible leak of uninitialized memory. This attack appear to be exploitable via A malformed packet is received over the network by a Godot application that uses built-in serialization (e.g. game server, or game client). Could be triggered by multiplayer opponent. This vulnerability appears to have been fixed in 2.1.5, 3.0.6, master branch after commit feaf03421dda0213382b51aff07bd5a96b29487b.

## References
- https://godotengine.org/article/maintenance-release-godot-2-1-5
- https://godotengine.org/article/maintenance-release-godot-3-0-6
- https://github.com/godotengine/godot/issues/20558
