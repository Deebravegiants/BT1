# [H] CVE-2026-67991

## Summary
Severity: High
Advisory: CVE-2026-67991
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-67991
Type: osv

## Details
crmne/ruby_llm at commit fa6f279847d6d7027814539d9c0dfc3bbdfd2a83 contains a polynomial-time regular expression denial-of-service condition in RubyLLM::Utils.underscore on Ruby 3.1.x. A very long crafted class, agent, or tool name can cause excessive CPU consumption and a denial of service.

## References
- https://gist.github.com/Zykis1024/9f2d68fa3fd4e3a0ab83063bbe61a8e2
- https://github.com/crmne/ruby_llm/blob/fa6f279847d6d7027814539d9c0dfc3bbdfd2a83/lib/ruby_llm/utils.rb#L13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67991.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67991
- https://github.com/crmne/ruby_llm/commit/9d75b033d7d00c4e1baa9b0afb4828faa8bd6602
- https://github.com/crmne/ruby_llm
