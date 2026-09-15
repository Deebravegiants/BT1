# [H] BIT-etcd-2022-34038

## Summary
Severity: High
Advisory: BIT-etcd-2022-34038
Aliases: CVE-2022-34038
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-etcd-2022-34038
Type: osv

## Affected
- Bitnami: `etcd` — affected >=3.5.4 <3.5.5

## Details
Etcd v3.5.4 allows remote attackers to cause a denial of service via function PageWriter.write in pagewriter.go. NOTE: the vendor's position is that this is not a vulnerability.

## References
- https://github.com/etcd-io/etcd/pull/14022
- https://github.com/etcd-io/etcd/pull/14452
- https://github.com/golang/vulndb/issues/2016#issuecomment-1698677762
- https://go-review.googlesource.com/c/vulndb/+/524456
- https://go-review.googlesource.com/c/vulndb/+/524456/2/data/excluded/GO-2023-2016.yaml
- https://nvd.nist.gov/vuln/detail/CVE-2022-34038
