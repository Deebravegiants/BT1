# [H] CKAN is vulnerable to session secret shared across instances using Docker images

## Summary
Severity: High
Advisory: CVE-2023-22746
Aliases: GHSA-pr8j-v4c8-h62x
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2023-02-03
Source: https://osv.dev/vulnerability/CVE-2023-22746
Type: osv

## Details
CKAN is an open-source DMS (data management system) for powering data hubs and data portals. When creating a new container based on one of the Docker images listed below, the same secret key was being used by default. If the users didn't set a custom value via environment variables in the `.env` file, that key was shared across different CKAN instances, making it easy to forge authentication requests. Users overriding the default secret key in their own `.env` file are not affected by this issue. Note that the legacy images (ckan/ckan) located in the main CKAN repo are not affected by this issue. The affected images are ckan/ckan-docker, (ckan/ckan-base images), okfn/docker-ckan (openknowledge/ckan-base and openknowledge/ckan-dev images)
keitaroinc/docker-ckan (keitaro/ckan images).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22746.json
- https://github.com/ckan/ckan/security/advisories/GHSA-pr8j-v4c8-h62x
- https://nvd.nist.gov/vuln/detail/CVE-2023-22746
- https://github.com/ckan/ckan/commit/44af0f0a148fcc0e0fbcf02fe69b7db13459a84b
- https://github.com/ckan/ckan/commit/4c22c135fa486afa13855d1cdb9765eaf418d2aa
