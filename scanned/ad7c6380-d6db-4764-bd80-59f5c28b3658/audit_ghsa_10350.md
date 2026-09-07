# [C] OpenC3 COSMOS has SQL Injection in QuestDB Time-Series Database

## Summary
Severity: Critical
Advisory: GHSA-v529-vhwc-wfc5
CVE: CVE-2026-42087
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-v529-vhwc-wfc5
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=6.7.0 <7.0.0-rc3

## Details
**Vulnerability Type: CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
Attack type: Authenticated remote
Impact: Telemetry data disclosure and deletion
Affected components: openc3-tsdb (QuestDB)**

A SQL injection vulnerability exists in the Time-Series Database (TSDB) component of COSMOS. The `tsdb_lookup` function in the `cvt_model.rb` file directly places user-supplied input into a SQL query without sanitizing the input. As a result, a user can break out of the initial SQL statement and execute arbitrary SQL commands, including deleting data. 
 
<img width="940" height="719" alt="image" src="https://github.com/user-attachments/assets/2c2dd294-6192-49d3-b670-fd7b82c05be0" />

Figure 1: Source code vulnerable to SQL injection
Additionally, the `get_tlm_values` RPC endpoint only requires “tlm” permissions, allowing any user with the Admin, Operator, Viewer, or Runner roles to send a request to the TSDB. This permission is defined in roles-permissions.md to allow for the user to view telemetry data, but this vulnerability also allows them to delete data and tables.
 
<img width="940" height="410" alt="image" src="https://github.com/user-attachments/assets/40be7e8d-51f9-442d-bbd7-77c8488a2f78" />

Figure 2: Source code showing the required permissions for the `get_tlm_values` endpoint
Sending a normal request to the endpoint brings back a single array of values for the parameter:
 
<img width="944" height="481" alt="image" src="https://github.com/user-attachments/assets/23678f17-6bdf-41c1-81bc-ace5a8daa7e5" />

Figure 3: A normal request to the `get_tlm_values` endpoint
However, sending a specially crafted request within the start_time variable brings back all the data in the database:
 
<img width="944" height="432" alt="image" src="https://github.com/user-attachments/assets/bd5ecc87-ba9c-43f0-b196-91062b9c395a" />

Figure 4: The request and response after sending the SQL injection payload
This payload can be modified to executes SQL commands in the TSDB.
 
<img width="944" height="425" alt="image" src="https://github.com/user-attachments/assets/70c3c88e-9ed6-4542-bfb4-e77abb002c15" />

Figure 5: SQL injection used to execute arbitrary SQL command
The user can then delete all the historical data in the database:
 
<img width="944" height="496" alt="image" src="https://github.com/user-attachments/assets/f2dc1fa6-5fe0-4232-867a-a65776f108ee" />

Figure 6: Example payload dropping the tables
###	Steps to Reproduce
1.	Capture a JSON-RPC request to the `get_tlm_values` endpoint.
2.	Add the `start_time` key to the request body and place the following in the value:
```sql
‘ OR 1=1 --
```
3.	Retrieve all database data.
###	Recommendations
•	Sanitize all user-supplied input before executing it
•	Use prepared statements with parameterized queries when executing SQL statements

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-v529-vhwc-wfc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-42087
- https://github.com/OpenC3/cosmos/commit/9ba60c09c8836a37a2e4ea67ab35fe403e041415
- https://github.com/OpenC3/cosmos
- https://github.com/OpenC3/cosmos/releases/tag/v7.0.0-rc3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openc3/CVE-2026-42087.yml
