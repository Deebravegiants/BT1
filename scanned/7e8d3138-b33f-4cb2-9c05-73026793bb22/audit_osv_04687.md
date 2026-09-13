# [C] Kibana arbitrary code execution via YAML deserialization

## Summary
Severity: Critical
Advisory: BIT-elk-2024-37285
Aliases: BIT-kibana-2024-37285, CVE-2024-37285
Ecosystem: Bitnami
Published: 2024-11-16
Source: https://osv.dev/vulnerability/BIT-elk-2024-37285
Type: osv

## Affected
- Bitnami: `elk` — affected >=8.10.0 <8.15.1

## Details
A deserialization issue in Kibana can lead to arbitrary code execution when Kibana attempts to parse a YAML document containing a crafted payload. A successful attack requires a malicious user to have a combination of both specific  Elasticsearch indices privileges https://www.elastic.co/guide/en/elasticsearch/reference/current/defining-roles.html#roles-indices-priv  and  Kibana privileges https://www.elastic.co/guide/en/fleet/current/fleet-roles-and-privileges.html  assigned to them.



The following Elasticsearch indices permissions are required

  *  write privilege on the system indices .kibana_ingest*
  *  The allow_restricted_indices flag is set to true


Any of the following Kibana privileges are additionally required

  *  Under Fleet the All privilege is granted
  *  Under Integration the Read or All privilege is granted
  *  Access to the fleet-setup privilege is gained through the Fleet Server’s service account token

## References
- https://discuss.elastic.co/t/kibana-8-15-1-security-update-esa-2024-27-esa-2024-28/366119
- https://nvd.nist.gov/vuln/detail/CVE-2024-37285
