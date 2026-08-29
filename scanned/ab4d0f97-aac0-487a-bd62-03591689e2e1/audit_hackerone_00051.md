# [H] CVE-2024-27281: RCE vulnerability with .rdoc_options in RDoc

## Summary
Severity: High
Program: Internet Bug Bounty
Weakness: N/A
Reporter: ooooooo_q
State: resolved
Disclosed: 2024-03-29T23:47:42.016Z
CVE: CVE-2024-27281
Source: https://hackerone.com/reports/2438265

## Details
I made a report at https://hackerone.com/reports/1187477

https://www.ruby-lang.org/en/news/2024/03/21/rce-rdoc-cve-2024-27281/

> An issue was discovered in RDoc 6.3.3 through 6.6.2, as distributed in Ruby 3.x through 3.3.0.
> When parsing .rdoc_options (used for configuration in RDoc) as a YAML file, object injection and resultant remote code execution are possible because there are no restrictions on the classes that can be restored.
> When loading the documentation cache, object injection and resultant remote code execution are also possible if there were a crafted cache.

## Impact

RCE is possible when the `rdoc` command is executed for a repository received from the external.
