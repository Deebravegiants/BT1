# [M] IP address leak via image proxy bypass in Zulip Server

## Summary
Severity: Medium
Advisory: CVE-2022-36048
Aliases: GHSA-vg5m-mf9x-j452
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-36048
Type: osv

## Details
Zulip is an open-source team collaboration tool with topic-based threading that combines email and chat. When displaying messages with embedded remote images, Zulip normally loads the image preview via a go-camo proxy server. However, an attacker who can send messages could include a crafted URL that tricks the server into embedding a remote image reference directly. This could allow the attacker to infer the viewer’s IP address and browser fingerprinting information. This vulnerability is fixed in Zulip Server 5.6. Zulip organizations with image and link previews [disabled](https://zulip.com/help/allow-image-link-previews) are not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36048.json
- https://github.com/zulip/zulip/security/advisories/GHSA-vg5m-mf9x-j452
- https://nvd.nist.gov/vuln/detail/CVE-2022-36048
