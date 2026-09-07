# [C] Files Accessible to External Parties in Opencast

## Summary
Severity: Critical
Advisory: GHSA-59g4-hpg3-3gcp
CVE: CVE-2021-43821
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-59g4-hpg3-3gcp
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-ingest-service-impl` — affected >=0 <10.6

## Details
Opencast before version 10.6 allows references to local file URLs in ingested media packages, allowing attackers to include local files from Opencast's host machines and making them available via the web interface.

### Impact

Before Opencast 10.6, Opencast would [open and include local files during ingests](https://github.com/opencast/opencast/blob/69952463971cf578363e3b97d8edaf334ff51253/modules/ingest-service-impl/src/main/java/org/opencastproject/ingest/impl/IngestServiceImpl.java#L1587). Attackers could exploit this to include most local files the process has read access to, extracting secrets from the host machine.

For example, to expose the `custom.properties` of develop.opencast.org via the asset manager, an attacker could have run:

```
curl -f -i -u admin:opencast \
  https://develop.opencast.org/ingest/addMediaPackage/fast \
  -F 'flavor=presenter/source'\
  -F mediaUri=file:///srv/opencast/opencast-dist-allinone/etc/custom.properties\
  -F title="custom.properties"  
```

An attacker would need to have the privileges required to add new media to exploit this. But these are often widely given.


### Patches

The issue has been fixed in Opencast 10.6 and 11.0.

### Workarounds

You can mitigate this issue by narrowing down the read access Opencast has to files on the file system using UNIX permissions or mandatory access control systems like SELinux. This cannot prevent access to files Opencast needs to read though and we highly recommend updating.

### References

-  [Example of problematic code](https://github.com/opencast/opencast/blob/69952463971cf578363e3b97d8edaf334ff51253/modules/ingest-service-impl/src/main/java/org/opencastproject/ingest/impl/IngestServiceImpl.java#L1587).
- [Patch fixing the issue](https://github.com/opencast/opencast/commit/65c46b9d3e8f045c544881059923134571897764)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
* Email us at [security@opencast.org](mailto:security@opencast.org)

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-59g4-hpg3-3gcp
- https://nvd.nist.gov/vuln/detail/CVE-2021-43821
- https://github.com/opencast/opencast/commit/65c46b9d3e8f045c544881059923134571897764
- https://github.com/opencast/opencast
- https://github.com/opencast/opencast/blob/69952463971cf578363e3b97d8edaf334ff51253/modules/ingest-service-impl/src/main/java/org/opencastproject/ingest/impl/IngestServiceImpl.java#L1587
- https://mvnrepository.com/artifact/org.opencastproject/opencast-ingest-service-impl
