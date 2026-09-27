# [M] CVE-2021-41865

## Summary
Severity: Medium
Advisory: CVE-2021-41865
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-07
Source: https://osv.dev/vulnerability/CVE-2021-41865
Type: osv

## Details
HashiCorp Nomad and Nomad Enterprise 1.1.1 through 1.1.5 allowed authenticated users with job submission capabilities to cause denial of service by submitting incomplete job specifications with a Consul mesh gateway and host networking mode. Fixed in 1.1.6.

## References
- https://discuss.hashicorp.com/t/hcsec-2021-26-nomad-denial-of-service-via-submission-of-incomplete-job-specification-using-consul-mesh-gateway-host-network/30311
