# [C] karo Metacharacter Handling Remote Command Execution

## Summary
Severity: Critical
Advisory: GHSA-qfwq-chf4-jvwg
CVE: CVE-2014-10075
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qfwq-chf4-jvwg
Type: github-advisory

## Affected
- RubyGems: `karo` — affected >=0

## Details
The karo gem through 2.5.2 for Ruby allows Remote command injection via the host field.

A flaw in `db.rb` is triggered when handling metacharacters. This may allow a remote attacker to execute arbitrary commands.

In particular lines 76 and 95 (as of `2014-06-01`) pass unsanitized user supplied input to the command line. 

```
73-      host = "{@configuration["user"]}@{@configuration["host"]}"
74-      cmd  = "ssh #{host} cat {server_db_config_file}"
75-
76:      server_db_config_output = `{cmd}`
79-
--
89- def drop_and_create_local_database(local_db_config)
90-      command = case local_db_config["adapter"]
91-      when "mysql2"
93-      when "postgresql"
95-          dropdb -h #{local_db_config["host"]} -U #{local_db_config["username"]} --if-exists #{local_db_config["database"]}
```

If this gem is used in the context of a rails application malicious input could lead to remote command injection. As of version 2.5.2 the affected code lines have not changed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-10075
- https://github.com/rahult/karo
- https://github.com/rahult/karo/blob/master/lib/karo/db.rb#L76
- https://github.com/rahult/karo/blob/master/lib/karo/db.rb#L95
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/karo/CVE-2014-10075.yml
- http://www.vapid.dhs.org/advisories/karo-2.3.8.html
- http://www.vapidlabs.com/advisory.php?v=63
