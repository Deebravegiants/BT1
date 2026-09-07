# [M] Parsl Monitoring Visualization Vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-f2mf-q878-gh58
CVE: CVE-2026-21892
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-01-06
Source: https://github.com/advisories/GHSA-f2mf-q878-gh58
Type: github-advisory

## Affected
- PyPI: `parsl` — affected >=0 <2026.01.05

## Details
**Affected Product:** Parsl (Python Parallel Scripting Library)

**Component:** parsl.monitoring.visualization

**Vulnerability Type:** SQL Injection (CWE-89)

**Severity:** High (CVSS Rating Recommended: 7.5 - 8.6)

**URL:** [https://github.com/Parsl/parsl/blob/master/parsl/monitoring/visualization/views.py]( https://github.com/Parsl/parsl/blob/master/parsl/monitoring/visualization/views.py)

**Summary**

A SQL Injection vulnerability exists in the parsl-visualize component of the Parsl library. The application constructs SQL queries using unsafe string formatting (Python % operator) with user-supplied input (workflow_id) directly from URL routes. This allows an unauthenticated attacker with access to the visualization dashboard to inject arbitrary SQL commands, potentially leading to data exfiltration or denial of service against the monitoring database.

**Root Cause Analysis**

The vulnerability is located in parsl/monitoring/visualization/views.py. Multiple route handlers take the workflow_id parameter from the URL and inject it directly into a raw SQL query string without sanitization or parameterization.

Vulnerable Code Snippet 1 

```
   query = """SELECT task.task_id, task.task_func_name, task.task_depends, status.task_status_name
               FROM task LEFT JOIN status
               ON task.task_id = status.task_id
               AND task.run_id = status.run_id
               AND status.timestamp = (SELECT MAX(status.timestamp)
                                       FROM status
                                       WHERE status.task_id = task.task_id and status.run_id = task.run_id
                                      )
               WHERE task.run_id='%s'""" % (workflow_id)
```

Vulnerable Code Snippet 2
```
df_task_tries = pd.read_sql_query("""SELECT ...
                                     WHERE task.task_id = try.task_id AND task.run_id='%s' and try.run_id='%s'"""
                                     % (workflow_id, workflow_id), db.engine) # <--- Vulnerable 
```

**Impact**

**Data Exfiltration:** An attacker can use UNION based injection to dump the entire contents of the monitoring database, including potentially sensitive environment variables, task parameters, or host information logged by the monitoring system.

**Access Control Bypass:** By injecting boolean logic (e.g., ' OR '1'='1), an attacker could bypass specific workflow filters to view data they are not authorized to see.

**Denial of Service:** Time-based attacks or resource-intensive queries (e.g., randomblob) could crash the visualization server or the database.

**Proof of Concept (PoC)**

**Prerequisites:**

Parsl installed with monitoring enabled (pip install 'parsl[monitoring,visualization]').

A running parsl-visualize server serving a database with at least one recorded workflow.

**Reproduction Steps:**

Identify a valid workflow ID (or use a known ID like default-run or a UUID).

Navigate to the dag_group_by_states endpoint using the following manipulated URLs to confirm SQL logic control (Boolean-based Blind SQLi).

Test 1: Boolean FALSE (Graph Disappears)
Injecting a false condition (1=0) causes the query to return zero rows, resulting in an empty visualization.

`http://<server>:8080/workflow/<VALID_ID>'%20AND%20'1'='0/dag_group_by_states
`

Test 2: Boolean TRUE (Graph Reappears)
Injecting a true condition (1=1) restores the query logic, causing the graph to render correctly.

`http://<server>:8080/workflow/<VALID_ID>'%20AND%20'1'='1/dag_group_by_states
`

## References
- https://github.com/Parsl/parsl/security/advisories/GHSA-f2mf-q878-gh58
- https://nvd.nist.gov/vuln/detail/CVE-2026-21892
- https://github.com/Parsl/parsl/commit/013a928461e70f38a33258bd525a351ed828e974
- https://github.com/Parsl/parsl
