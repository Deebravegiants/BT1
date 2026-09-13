# [C] discordrb OS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8832-4mm5-x2r6
CVE: CVE-2023-28102
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-14
Source: https://github.com/advisories/GHSA-8832-4mm5-x2r6
Type: github-advisory

## Affected
- RubyGems: `discordrb` — affected >=0 <3.4.3

## Details
discordrb is an implementation of the Discord API using Ruby. In discordrb before commit `91e13043ffa` the `encoder.rb` file unsafely constructs a shell string using the file parameter, which can potentially leave clients of discordrb vulnerable to command injection. The library is not directly exploitable: the exploit requires that some client of the library calls the vulnerable method with user input. However, if unsafe input reaches the library method, then an attacker can execute arbitrary shell commands on the host machine. Full impact will depend on the permissions of the process running the `discordrb` library and will likely not be total system access. This issue has been addressed in code, but a new release of the `discordrb` gem has not been uploaded to rubygems. This issue is also tracked as `GHSL-2022-094`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28102
- https://github.com/shardlab/discordrb/commit/91e13043ffa89227c3fcdc3408f06da237d28c95
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/discordrb/CVE-2023-28102.yml
- https://github.com/shardlab/discordrb
- https://securitylab.github.com/advisories
- https://securitylab.github.com/advisories/GHSL-2022-094_discordrb
