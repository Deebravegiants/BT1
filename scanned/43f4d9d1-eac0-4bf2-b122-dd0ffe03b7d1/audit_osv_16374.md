# [H] CVE-2019-6250

## Summary
Severity: High
Advisory: CVE-2019-6250
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-13
Source: https://osv.dev/vulnerability/CVE-2019-6250
Type: osv

## Details
A pointer overflow, with code execution, was discovered in ZeroMQ libzmq (aka 0MQ) 4.2.x and 4.3.x before 4.3.1. A v2_decoder.cpp zmq::v2_decoder_t::size_ready integer overflow allows an authenticated attacker to overwrite an arbitrary amount of bytes beyond the bounds of a buffer, which can be leveraged to run arbitrary code on the target system. The memory layout allows the attacker to inject OS commands into a data structure located immediately after the problematic buffer (i.e., it is not necessary to use a typical buffer-overflow exploitation technique that changes the flow of control).

## References
- https://github.com/zeromq/libzmq/releases/tag/v4.3.1
- https://security.gentoo.org/glsa/201903-22
- https://www.debian.org/security/2019/dsa-4368
- https://github.com/zeromq/libzmq/issues/3351
