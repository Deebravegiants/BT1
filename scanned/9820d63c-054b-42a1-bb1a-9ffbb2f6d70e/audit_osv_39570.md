# [H] ipmi: Add limits to event and receive message requests

## Summary
Severity: High
Advisory: CVE-2026-46177
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46177
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipmi: Add limits to event and receive message requests

The driver would just fetch events and receive messages until the
BMC said it was done.  To avoid issues with BMCs that never say they are
done, add a limit of 10 fetches at a time.

In addition, an si interface has an attn state it can return from the
hardware which is supposed to cause a flag fetch to see if the driver
needs to fetch events or message or a few other things.  If the attn
bit gets stuck, it's a similar problem.  So allow messages in between
flag fetches so the driver itself doesn't get stuck.

This is a more general fix than the previous fix for the specific bad
BMC, but should fix the more general issue of a BMC that won't stop
saying it has data.

This has been there from the beginning of the driver.  It's not a bug
per-se, but it is accounting for bugs in BMCs.

## References
- https://git.kernel.org/stable/c/112df8e631636cafda64dcee4561daf09ce74a4a
- https://git.kernel.org/stable/c/304b56883b7eff73eb606c35d062c8101aaf5471
- https://git.kernel.org/stable/c/3d37d2165df9504ea99d9e6181552dc4d2d1ab37
- https://git.kernel.org/stable/c/67c44e0deba936d5edaebea356b4589eb43acb5c
- https://git.kernel.org/stable/c/9059dc94421e1d4f8e5844204608b37ebfddb3da
- https://git.kernel.org/stable/c/c024167fb00489baee08c72182ca2e7dc5fb9f20
- https://git.kernel.org/stable/c/c4cca236968683eb0d59abfb12d5c7e4d8514227
- https://git.kernel.org/stable/c/e20212b431bef217d3886b86bbc90cc3ed00de68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46177.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46177
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
