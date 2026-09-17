# [C] Use of Insufficiently Random Values in Railties Allows Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-m42h-mh85-4qgc
CVE: CVE-2019-5420
CWE: CWE-330, CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-03-13
Source: https://github.com/advisories/GHSA-m42h-mh85-4qgc
Type: github-advisory

## Affected
- RubyGems: `railties` — affected >=5.2.0 <5.2.2.1

## Details
# Possible Remote Code Execution Exploit in Rails Development Mode

Impact 
------ 
With some knowledge of a target application it is possible for an attacker to  guess the automatically generated development mode secret token.  This secret  token can be used in combination with other Rails internals to escalate to a remote code execution exploit. 

All users running an affected release should either upgrade or use one of the workarounds immediately. 

Releases 
-------- 
The 6.0.0.beta3 and 5.2.2.1 releases are available at the normal locations. 

Workarounds 
----------- 
This issue can be mitigated by specifying a secret key in development mode. 
In "config/environments/development.rb" add this: 

```
  config.secret_key_base = SecureRandom.hex(64) 
```

Please note that only the 5.2.x, 5.1.x, 5.0.x, and 4.2.x series are supported at present. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases. 

Credits 
------- 
Thanks to ooooooo_q

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5420
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/railties/CVE-2019-5420.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/IsQKvDqZdKw
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Y43636TH4D6T46IC6N2RQVJTRFJAAYGA
- https://weblog.rubyonrails.org/2019/3/13/Rails-4-2-5-1-5-1-6-2-have-been-released
- https://www.exploit-db.com/exploits/46785
- http://packetstormsecurity.com/files/152704/Ruby-On-Rails-DoubleTap-Development-Mode-secret_key_base-Remote-Code-Execution.html
