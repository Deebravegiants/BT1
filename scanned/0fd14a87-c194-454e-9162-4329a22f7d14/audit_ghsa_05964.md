# [H] praisonaiagents vulnerable to SSRF in web_crawl tool via redirect-following and DNS rebinding (validate-then-fetch gap)

## Summary
Severity: High
Advisory: GHSA-vg6p-v9vm-6fgj
CVE: CVE-2026-55524
CWE: CWE-367, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-vg6p-v9vm-6fgj
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.58

## Details
The web_crawl tool performs its SSRF check only on the initial URL: it resolves the hostname once
with socket.gethostbyname and rejects private/loopback/link-local results. It then passes the URL to
a fetcher that uses httpx.Client(follow_redirects=True) - or urllib.request.urlopen when httpx is
absent, which also follows redirects - and re-resolves the hostname at connect time, with no further
validation. This validate-here/fetch-there gap is bypassable two independent ways: HTTP redirects and
DNS rebinding.

Affected code: src/praisonai-agents/praisonaiagents/tools/web_crawl_tools.py
- Single-shot validation (lines 229-238):
    if os.environ.get("ALLOW_LOCAL_CRAWL") != "true":
        ip_str = socket.gethostbyname(hostname)            # resolved ONCE, at validation time
        ip = ipaddress.ip_address(ip_str)
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
            continue                                       # rejected
    url_list.append(u)
- Vulnerable fetch (_crawl_with_httpx, lines 142 / 149): follows redirects, re-resolves DNS, no re-check:
    with httpx.Client(follow_redirects=True, timeout=30.0) as client: response = client.get(url)
    # fallback: urllib.request.urlopen(url, timeout=30)  (also follows redirects by default)
- web_crawl / crawl_web are registered tools (tools/__init__.py:156-157); httpx is the default fallback
  provider (dispatch at web_crawl_tools.py:269).

The two bypasses:
1) Redirect: validation approves an attacker domain resolving to a public IP; attacker server replies
   302 Location: http://169.254.169.254/... (or any internal host); the fetcher follows it unchecked.
2) DNS rebinding (TOCTOU): validator's gethostbyname and fetcher's connect-time resolution are
   independent; a low-TTL attacker domain answers public to the validator and private/loopback to fetch.

Impact:
An agent with web_crawl - driven by direct input or indirect prompt injection - can be made to read
internal-only HTTP services and cloud instance-metadata endpoints (e.g. IAM credentials), with the
response body returned in the tool output. Scope is Changed because the request pivots into the
internal network.

Proof of concept:
A PoC drives the real web_crawl() (httpx absent -> genuine urllib fallback). It runs a loopback
"internal metadata" service and a loopback attacker redirector, substituting DNS only to stand in
for "attacker owns a public domain" / offline routing - the redirect-following and connect-time
re-resolution are the repo's own behavior. Observed:
  CONTROL: web_crawl("http://127.0.0.1:.../meta-data/")  -> blocked (validator works)
  PoC 1A (redirect):  attacker.example approved (public); 302 -> loopback metadata
                      -> result.content leaks {"AccessKeyId":"ASIA_FAKE_STOLEN_CREDENTIAL_..."}
  PoC 1B (rebinding): gethostbyname(rebind.example)->public (allowed); connect->127.0.0.1
                      -> same secret leaked
The control proves the validator blocks a direct loopback request, so the bypasses are genuine.

Remediation:
Resolve the hostname once, validate that IP, and connect to that exact validated IP (pin it) rather
than re-resolving. Disable redirect following (follow_redirects=False; for urllib use a redirect
handler that re-validates), or re-validate every redirect hop's resolved IP. Apply the deny check to
both the validator and the actual socket target. file_tools.py:364 already uses follow_redirects=False
and is the correct pattern to propagate.

Distinct from prior advisories:
The accepted SSRF advisories concern host-string parsing in different code — alternate loopback
encodings in spider_tools (GHSA-5c6w-wwfq-7qqm) and the CLI @url feature (GHSA-5cxw-77wg-jrf3). This
is in the web_crawl tool, which neither advisory names, and the mechanisms (redirect-following and DNS
rebinding) differ categorically from host-string encoding; the spider_tools _host_is_blocked hardening
does not apply to this tool.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-vg6p-v9vm-6fgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-55524
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
