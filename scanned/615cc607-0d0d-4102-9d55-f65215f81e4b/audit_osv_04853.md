# [C] Fluentd vulnerable to remote code execution due to insecure deserialization (in non-default configuration)

## Summary
Severity: Critical
Advisory: BIT-fluentd-2022-39379
Aliases: CVE-2022-39379, GHSA-fppq-mj76-fpj2
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-fluentd-2022-39379
Type: osv

## Affected
- Bitnami: `fluentd` — affected >=1.13.2 <1.15.3

## Details
Fluentd collects events from various data sources and writes them to files, RDBMS, NoSQL, IaaS, SaaS, Hadoop and so on. A remote code execution (RCE) vulnerability in non-default configurations of Fluentd allows unauthenticated attackers to execute arbitrary code via specially crafted JSON payloads. Fluentd setups are only affected if the environment variable `FLUENT_OJ_OPTION_MODE` is explicitly set to `object`. Please note: The option FLUENT_OJ_OPTION_MODE was introduced in Fluentd version 1.13.2. Earlier versions of Fluentd are not affected by this vulnerability. This issue was patched in version 1.15.3. As a workaround do not use `FLUENT_OJ_OPTION_MODE=object`.

## References
- https://github.com/fluent/fluentd/commit/48e5b85dab1b6d4c273090d538fc11b3f2fd8135
- https://github.com/fluent/fluentd/security/advisories/GHSA-fppq-mj76-fpj2
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MYD5QV66OLDHES6IKVYYM3Y3YID3VVCO/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39379
