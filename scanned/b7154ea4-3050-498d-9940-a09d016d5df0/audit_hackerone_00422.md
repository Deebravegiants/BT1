# [H] Request Hijacking Vulnerability in RubyGems 2.6.11 and earlier

## Summary
Severity: High
Program: RubyGems
Weakness: Code Injection
Reporter: claudijd
State: resolved
Disclosed: 2017-08-30T23:36:42.991Z
CVE: CVE-2017-0902, CVE-2015-3900, CVE-2015-4020
Source: https://hackerone.com/reports/218088

## Details
**Description:**

The RubyGems client supports a gem server API discovery functionality,
which is used when pushing or pulling gems to a gem distribution/hosting
server, like RubyGems.org.  This functionality is provided via a SRV DNS
request to the users gem source hostname prepended with "_rubygems._tcp.".
The response to this request tells the RubyGems client (aka: the gem
command) where the users gem server API is.  In the default RubyGems
scenario, with a gem source of https://rubygems.org, the users SRV DNS
request and reply will look like this:

    ~ $ dig srv _rubygems._tcp.rubygems.org +short
    0 1 80 api.rubygems.org.

Due to a deficiency in DNS response verification, a MiTM positioned 
attacker can poison the DNS response to this record response and force
the client to unknowingly download and install Ruby gems from an attacker
controlled gem server in an alternate security domain.  An example of
such a scenario would look like so:

    ~ $ dig _rubygems._tcp.rubygems.org SRV +short
    0 0 53 evil.com/api.rubygems.com.

In such a scenario, the attacker is able to serve the client malicious gem
content, resulting in trivial remote code execution scenarios.  For
example, the attacker could simply modify the gem source code and trigger
code execution via the extensions API at install time on the client machine
(a gem trojaning technique described by Ben Smith in his "Hacking with
Gems" presentation at Aloha Ruby Conference in 2012 -
https://www.youtube.com/watch?v=z-5bO0Q1J9s)/

This vulnerability has the same net effect/impact as [CVE-2015-3900](https://nvd.nist.gov/vuln/detail/CVE-2015-3900) and
[CVE-2015-4020](https://nvd.nist.gov/vuln/detail/CVE-2015-4020).

**Affected method in Gem::RemoteFetcher:**

https://github.com/rubygems/rubygems/blob/5096fa35c1ca3e0a7d175aaf9d77cd93114fd977/lib/rubygems/remote_fetcher.rb#L101-L119


_Trimmed to 38 lines — full report: https://hackerone.com/reports/218088_
