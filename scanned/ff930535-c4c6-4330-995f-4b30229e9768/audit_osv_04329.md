# [C] Remote Code Execution Vulnerability in Packaging

## Summary
Severity: Critical
Advisory: BIT-couchdb-2022-24706
Aliases: CVE-2022-24706
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-couchdb-2022-24706
Type: osv

## Affected
- Bitnami: `couchdb` — affected >=0 <3.2.2

## Details
In Apache CouchDB prior to 3.2.2, an attacker can access an improperly secured default installation without authenticating and gain admin privileges. The CouchDB documentation has always made recommendations for properly securing an installation, including recommending using a firewall in front of all CouchDB installations.

## References
- http://packetstormsecurity.com/files/167032/Apache-CouchDB-3.2.1-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/169702/Apache-CouchDB-Erlang-Remote-Code-Execution.html
- http://www.openwall.com/lists/oss-security/2022/04/26/1
- http://www.openwall.com/lists/oss-security/2022/05/09/1
- http://www.openwall.com/lists/oss-security/2022/05/09/2
- http://www.openwall.com/lists/oss-security/2022/05/09/3
- http://www.openwall.com/lists/oss-security/2022/05/09/4
- https://docs.couchdb.org/en/3.2.2/setup/cluster.html
- https://lists.apache.org/thread/w24wo0h8nlctfps65txvk0oc5hdcnv00
- https://medium.com/%40_sadshade/couchdb-erlang-and-cookies-rce-on-default-settings-b1e9173a4bcd
- https://nvd.nist.gov/vuln/detail/CVE-2022-24706
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-24706
