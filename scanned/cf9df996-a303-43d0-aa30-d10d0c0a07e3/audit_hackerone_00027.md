# [C] SQL Injection in Django ORM via Unvalidated `_connector` in Q Objects

## Summary
Severity: Critical (CVSS 9.8)
Program: Django
Weakness: SQL Injection
Reporter: cyberstan
State: resolved
Disclosed: 2025-11-06T21:09:42.024Z
Source: https://hackerone.com/reports/3335709

## Details
### Summary

A **critical** SQL injection vulnerability exists in the Django ORM's handling of `Q` objects. The internal `WhereNode.as_sql` method uses unsafe string formatting to inject the query connector (e.g., 'AND') into the raw SQL query. An attacker can control this connector value via the `_connector` key when a `Q` object is created using dictionary unpacking (e.g., `Q(**user_input)`). This allows the attacker to inject arbitrary SQL into the `WHERE` clause, completely bypassing the ORM's parameterization safeguards, leading to filter bypass and full data exfiltration from the queried model.

---

### Vulnerability Details

The root cause of the vulnerability is in `django/db/models/sql/where.py` within the `WhereNode.as_sql` method. This method is responsible for joining multiple filter conditions together. The code uses unsafe string formatting to insert the connector:

```python
# Simplified representation of the vulnerable code in WhereNode.as_sql
conn = ' %s ' % self.connector
```

The method does not perform any validation or sanitization on the `self.connector` attribute before embedding it into the query. The framework allows a developer to specify this connector via the `_connector` argument when initializing a `Q` object. A common pattern in applications with complex filtering, such as those with a search API, is to accept a dictionary of filters and unpack it directly. This pattern is highly vulnerable:

```python
# An example of a vulnerable application pattern
filter_dictionary = request.json.get('filters', {{}})
query = Q(**filter_dictionary) # VULNERABLE LINE
results = User.objects.filter(query)
```

If an attacker controls the contents of `filter_dictionary`, they can insert a `_connector` key with a malicious SQL payload. This payload is then injected directly into the query's structure.

---

### POC

1. First create a new django project and the app. Also make sure you add the webapp to the installed apps within settings.py.
```bash
django-admin startproject sqli .
python manage.py startapp webapp
```
```python
# sqli/settings.py

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3335709_
