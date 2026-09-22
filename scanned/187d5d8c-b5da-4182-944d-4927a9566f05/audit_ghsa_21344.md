# [C] MySQL JDBC deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-q4qq-jhjv-7rh2
CVE: CVE-2022-39312
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-q4qq-jhjv-7rh2
Type: github-advisory

## Affected
- Maven: `io.dataease:dataease-plugin-common` — affected >=0 <1.15.2

## Details
### Impact

In Dataease, the Mysql data source in the data source function can customize the JDBC connection parameters and the Mysql server target to be connected.
![6fc8d5c539807157ee471464b184ab66](https://user-images.githubusercontent.com/13026505/195741851-19f32efb-4391-428a-949f-3d11849f417a.png)

In `backend/src/main/java/io/dataease/provider/datasource/JdbcProvider.java`, MysqlConfiguration class don't filter any parameters, directly concat user input.
```java
@Getter
@Setter
public class MysqlConfiguration extends JdbcConfiguration {

    private String driver = "com.mysql.jdbc.Driver";
    private String extraParams = "characterEncoding=UTF-8&connectTimeout=5000&useSSL=false&allowPublicKeyRetrieval=true&zeroDateTimeBehavior=convertToNull";

    public String getJdbc() {
        if(StringUtils.isEmpty(extraParams.trim())){
            return "jdbc:mysql://HOSTNAME:PORT/DATABASE"
                    .replace("HOSTNAME", getHost().trim())
                    .replace("PORT", getPort().toString().trim())
                    .replace("DATABASE", getDataBase().trim());
        }else {
            return "jdbc:mysql://HOSTNAME:PORT/DATABASE?EXTRA_PARAMS"
                    .replace("HOSTNAME", getHost().trim())
                    .replace("PORT", getPort().toString().trim())
                    .replace("DATABASE", getDataBase().trim())
                    .replace("EXTRA_PARAMS", getExtraParams().trim());
        }
    }
}
```
So, if the attack add some parameters in JDBC url, and connect to evil mysql server, he can trigger the mysql jdbc deserialization vulnerability, and eventually the attacker can execute through the deserialization vulnerability system commands and obtain server privileges.

Affected versions: < 1.15.2

### Patches

The vulnerability has been fixed in v1.15.2.
https://github.com/dataease/dataease/blob/6c3a011955c5c753ffd616d030bea5db4793c51c/backend/src/main/java/io/dataease/dto/datasource/MysqlConfiguration.java#L19
the MysqlConfiguration class use `illegalParameters` filter illegal parameters to fix this vulnerability.
```
@Getter
@Setter
public class MysqlConfiguration extends JdbcConfiguration {

    private String driver = "com.mysql.jdbc.Driver";
    private String extraParams = "characterEncoding=UTF-8&connectTimeout=5000&useSSL=false&allowPublicKeyRetrieval=true&zeroDateTimeBehavior=convertToNull";
    private List<String> illegalParameters = Arrays.asList("autoDeserialize", "queryInterceptors", "statementInterceptors", "detectCustomCollations");

    public String getJdbc() {
        if (StringUtils.isEmpty(extraParams.trim())) {
            return "jdbc:mysql://HOSTNAME:PORT/DATABASE"
                    .replace("HOSTNAME", getHost().trim())
                    .replace("PORT", getPort().toString().trim())
                    .replace("DATABASE", getDataBase().trim());
        } else {
            for (String illegalParameter : illegalParameters) {
                if (getExtraParams().contains(illegalParameter)) {
                    throw new RuntimeException("Illegal parameter: " + illegalParameter);
                }
            }

            return "jdbc:mysql://HOSTNAME:PORT/DATABASE?EXTRA_PARAMS"
                    .replace("HOSTNAME", getHost().trim())
                    .replace("PORT", getPort().toString().trim())
                    .replace("DATABASE", getDataBase().trim())
                    .replace("EXTRA_PARAMS", getExtraParams().trim());
        }
    }
}
```

### Workarounds

It is recommended to upgrade the version to v1.15.2.


### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/dataease/dataease](https://github.com/dataease/dataease)
* Email us at [wei@fit2cloud.com](mailto:wei@fit2cloud.com)

## References
- https://github.com/dataease/dataease/security/advisories/GHSA-q4qq-jhjv-7rh2
- https://nvd.nist.gov/vuln/detail/CVE-2022-39312
- https://github.com/dataease/dataease/pull/3328
- https://github.com/dataease/dataease/commit/956ee2d6c9e81349a60aef435efc046888e10a6d
- https://github.com/dataease/dataease
- https://github.com/dataease/dataease/releases/tag/v1.15.2
