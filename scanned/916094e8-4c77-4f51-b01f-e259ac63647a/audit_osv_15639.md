# [H] CVE-2019-18277

## Summary
Severity: High
Advisory: CVE-2019-18277
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-18277
Type: osv

## Details
A flaw was found in HAProxy before 2.0.6. In legacy mode, messages featuring a transfer-encoding header missing the "chunked" value were not being correctly rejected. The impact was limited but if combined with the "http-reuse always" setting, it could be used to help construct an HTTP request smuggling attack against a vulnerable component employing a lenient parser that would ignore the content-length header as soon as it saw a transfer-encoding one (even if not entirely valid according to the specification).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00019.html
- https://git.haproxy.org/?p=haproxy-2.0.git%3Ba=commit%3Bh=196a7df44d8129d1adc795da020b722614d6a581
- https://lists.debian.org/debian-lts-announce/2022/05/msg00045.html
- https://usn.ubuntu.com/4174-1/
- https://www.mail-archive.com/haproxy%40formilux.org/msg34926.html
- https://nathandavison.com/blog/haproxy-http-request-smuggling
