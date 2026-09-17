# [H] Puma's Keepalive Connections Causing Denial Of Service

## Summary
Severity: High
Advisory: GHSA-q28m-8xjw-8vr5
CVE: CVE-2021-29509
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-q28m-8xjw-8vr5
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=0 <4.3.8
- RubyGems: `puma` — affected >=5.0.0 <5.3.1

## Details
This vulnerability is related to [CVE-2019-16770](https://github.com/puma/puma/security/advisories/GHSA-7xx3-m584-x994).

### Impact

The fix for CVE-2019-16770 was incomplete. The original fix only protected existing connections that had already been accepted from having their requests starved by greedy persistent-connections saturating all threads in the same process. However, new connections may still be starved by greedy persistent-connections saturating all threads in all processes in the cluster.

A `puma` server which received more concurrent `keep-alive` connections than the server had threads in its threadpool would service only a subset of connections, denying service to the unserved connections.

### Patches

This problem has been fixed in `puma` 4.3.8 and 5.3.1.

### Workarounds

Setting `queue_requests false` also fixes the issue. This is not advised when using `puma` without a reverse proxy, such as `nginx` or `apache`, because you will open yourself to slow client attacks (e.g. [slowloris](https://en.wikipedia.org/wiki/Slowloris_(computer_security))).

The fix is very small. [A git patch is available here](https://gist.github.com/nateberkopec/4b3ea5676c0d70cbb37c82d54be25837) for those using [unsupported versions](https://github.com/puma/puma/security/policy#supported-versions) of Puma.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [Puma](https://github.com/puma/puma).
* To report problems with this fix or to report another vulnerability, see [our security policy.](https://github.com/puma/puma/security/policy)

### Acknowledgements

Thank you to @MSP-Greg, @wjordan and @evanphx for their review on this issue. 

Thank you to @ioquatix for providing a modified fork of `wrk` which made debugging this issue much easier.

## References
- https://github.com/puma/puma/security/advisories/GHSA-q28m-8xjw-8vr5
- https://nvd.nist.gov/vuln/detail/CVE-2021-29509
- https://gist.github.com/nateberkopec/4b3ea5676c0d70cbb37c82d54be25837
- https://github.com/puma/puma
- https://github.com/puma/puma/security/policy
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2021-29509.yml
- https://lists.debian.org/debian-lts-announce/2022/08/msg00015.html
- https://rubygems.org/gems/puma
- https://security.gentoo.org/glsa/202208-28
