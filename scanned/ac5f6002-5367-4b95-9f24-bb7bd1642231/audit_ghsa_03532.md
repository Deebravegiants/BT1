# [M] Possible request smuggling in HTTP/2 due missing validation of content-length

## Summary
Severity: Medium
Advisory: GHSA-f256-j965-7f32
CVE: CVE-2021-21409
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-30
Source: https://github.com/advisories/GHSA-f256-j965-7f32
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http2` — affected >=4.0.0 <4.1.61.Final
- Maven: `org.jboss.netty:netty` — affected >=0
- Maven: `io.netty:netty` — affected >=0

## Details
### Impact
The content-length header is not correctly validated if the request only use a single Http2HeaderFrame with the endStream set to to true. This could lead to request smuggling if the request is proxied to a remote peer and translated to HTTP/1.1

This is a followup of https://github.com/netty/netty/security/advisories/GHSA-wm47-8v5p-wjpj which did miss to fix this one case. 

### Patches
This was fixed as part of 4.1.61.Final

### Workarounds
Validation can be done by the user before proxy the request by validating the header.

## References
- https://github.com/netty/netty/security/advisories/GHSA-f256-j965-7f32
- https://github.com/netty/netty/security/advisories/GHSA-wm47-8v5p-wjpj
- https://nvd.nist.gov/vuln/detail/CVE-2021-21409
- https://github.com/netty/netty/commit/b0fa4d5aab4215f3c22ce6123dd8dd5f38dc0432
- https://lists.apache.org/thread.html/re39391adcb863f0e9f3f15e7986255948f263f02e4700b82453e7102@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/re1911e05c08f3ec2bab85744d788773519a0afb27272a31ac2a0b4e8@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rdd5715f3ee5e3216d5e0083a07994f67da6dbb9731ce9e7a6389b18e@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rdd206d9dd7eb894cc089b37fe6edde2932de88d63a6d8368b44f5101@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rd8f72411fb75b98d366400ae789966373b5c3eb3f511e717caf3e49e@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rd4a6b7dec38ea6cd28b6f94bd4b312629a52b80be3786d5fb0e474bc@%3Cissues.kudu.apache.org%3E
- https://lists.apache.org/thread.html/rcae42fba06979934208bbd515584b241d3ad01d1bb8b063512644362@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rca0978b634a0c3ebee4126ec29c7f570b165fae3f8f3658754c1cbd3@%3Cissues.kudu.apache.org%3E
- https://lists.apache.org/thread.html/rbde2f13daf4911504f0eaea43eee4f42555241b5f6d9d71564b6c5fa@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rba2a9ef1d0af882ab58fadb336a58818495245dda43d32a7d7837187@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rafc77f9f03031297394f3d372ccea751b23576f8a2ae9b6b053894c5@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rac8cf45a1bab9ead5c9a860cbadd6faaeb7792203617b6ec3874736d@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/raa413040db6d2197593cc03edecfd168732e697119e6447b0a25d525@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra66e93703e3f4bd31bdfd0b6fb0c32ae96b528259bb1aa2b6d38e401@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/re4b0141939370304d676fe23774d0c6fbc584b648919825402d0cb39@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/re7c69756a102bebce8b8681882844a53e2f23975a189363e68ad0324@%3Cissues.flink.apache.org%3E
