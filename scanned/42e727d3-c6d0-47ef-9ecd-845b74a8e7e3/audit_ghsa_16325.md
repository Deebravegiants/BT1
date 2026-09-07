# [M] YARD's default template vulnerable to Cross-site Scripting in generated frames.html

## Summary
Severity: Medium
Advisory: GHSA-8mq4-9jjh-9xrc
CVE: CVE-2024-27285
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-8mq4-9jjh-9xrc
Type: github-advisory

## Affected
- RubyGems: `yard` — affected >=0 <0.9.36

## Details
### Summary
The "frames.html" file within the Yard Doc's generated documentation is vulnerable to Cross-Site Scripting (XSS) attacks due to inadequate sanitization of user input within the JavaScript segment of the "frames.erb" template file.

### Details
The vulnerability stems from mishandling user-controlled data retrieved from the URL hash in the embedded JavaScript code within the "frames.erb" template file. Specifically, the script lacks proper sanitization of the hash data before utilizing it to establish the top-level window's location. This oversight permits an attacker to inject malicious JavaScript payloads through carefully crafted URLs.

Snippet from "frames.erb":
(v0.9.34)
```erb
<script type="text/javascript">
  var match = unescape(window.location.hash).match(/^#!(.+)/);
  var name = match ? match[1] : '<%= url_for_main %>';
  name = name.replace(/^(\w+):\/\//, '').replace(/^\/\//, '');
  window.top.location = name;
</script>
```

(v0.9.35)
```erb
<script type="text/javascript">
  var match = decodeURIComponent(window.location.hash).match(/^#!(.+)/);
  var name = match ? match[1] : '<%= url_for_main %>';
  name = name.replace(/^((\w*):)?[\/\\]*/gm, '').trim();
  window.top.location.replace(name)
</script>
```

### PoC (Proof of Concept)
To exploit this vulnerability:
1. Gain access to the generated Yard Doc.
2. Locate and access the "frames.html" file.
3. Construct a URL containing the malicious payload in the hash segment, for instance: `#!javascript:xss` for v0.9.34, and `#:javascript:xss` for v0.9.35

### Impact
This XSS vulnerability presents a substantial threat by enabling an attacker to execute arbitrary JavaScript code within the user's session context. Potential ramifications include session hijacking, theft of sensitive data, unauthorized access to user accounts, and defacement of websites. Any user visiting the compromised page is susceptible to exploitation. It is critical to promptly address this vulnerability to mitigate potential harm to users and preserve the application's integrity.

## References
- https://github.com/lsegal/yard/security/advisories/GHSA-8mq4-9jjh-9xrc
- https://nvd.nist.gov/vuln/detail/CVE-2024-27285
- https://github.com/lsegal/yard/pull/1538
- https://github.com/lsegal/yard/commit/1fcb2d8b316caf8779cfdcf910715e9ab583f0aa
- https://github.com/lsegal/yard/commit/2069e2bf08293bda2fcc78f7d0698af6354054be
- https://github.com/advisories/GHSA-8mq4-9jjh-9xrc
- https://github.com/lsegal/yard
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/yard/CVE-2024-27285.yml
- https://lists.debian.org/debian-lts-announce/2024/03/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MR3Z2E2UIZZ7YOR7R645EVSBGWMB2RGA
